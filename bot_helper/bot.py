import os
import sys
import logging
import asyncio

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode, ContentType
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold, hitalic


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    BOT_TOKEN = os.getenv("BOT_HELPER_TOKEN")
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
    REQUEST_TIMEOUT = 3600
    MAX_TICKETS_PER_USER = 3

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

class TempDB:
    users: Dict[int, Dict] = {}
    tickets: Dict[int, Dict] = {}
    counters = {'ticket_id': 1, 'user_id': 1}
    statistics = {
        'total_tickets': 0,
        'response_times': [],
        'categories': defaultdict(int),
        'priorities': defaultdict(int)
    }
db = TempDB()

class TicketStatus:
    NEW = "🆕 Новый"
    OPEN = "🟡 Открыт"
    IN_PROGRESS = "🔵 В работе"
    CLOSED = "🟢 Закрыт"
    URGENT = "🔴 Срочный"

class UserStates(StatesGroup):
    select_category = State()
    create_ticket = State()
    add_comment = State()

class AdminStates(StatesGroup):
    answer_ticket = State()
    manage_ticket = State()

def main_menu(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📨 Новый запрос", callback_data="new_ticket")
    builder.button(text="📂 Мои запросы", callback_data="my_tickets")
    if user_id in Config.ADMIN_IDS:
        builder.button(text="🛠 Панель админа", callback_data="admin_panel")
    builder.adjust(1)
    return builder.as_markup()

def ticket_priority_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔴 Высокий", callback_data="urgent")
    builder.button(text="🟡 Средний", callback_data="medium")
    builder.button(text="🟢 Низкий", callback_data="low")
    builder.adjust(3)
    return builder.as_markup()

def ticket_actions(ticket_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Ответить", callback_data=f"reply_{ticket_id}")
    builder.button(text="📌 Статус", callback_data=f"status_{ticket_id}")
    builder.button(text="🚫 Закрыть", callback_data=f"close_{ticket_id}")
    builder.adjust(2)
    return builder.as_markup()

def tickets_list_kb(tickets: List[int], page: int = 0, items_per_page: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    paginated_tickets = tickets[start_idx:end_idx]
    
    for ticket_id in paginated_tickets:
        ticket = db.tickets[ticket_id]
        builder.button(
            text=f"#{ticket_id} {ticket['status']}",
            callback_data=f"view_ticket_{ticket_id}"
        )
    
    if page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"page_{page-1}")
    if end_idx < len(tickets):
        builder.button(text="Вперед ➡️", callback_data=f"page_{page+1}")
    
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(1, 2)
    return builder.as_markup()

@dp.message(CommandStart())
async def start(message: Message):
    user = message.from_user
    if user.id not in db.users:
        db.users[user.id] = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'tickets': [],
            'blocked': False
        }
    
    await message.answer(
        f"👋 Привет, {user.full_name}!\n"
        "Выберите действие:",
        reply_markup=main_menu(user.id)
    )

@dp.callback_query(F.data == "new_ticket")
async def new_ticket(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id not in db.users:
        db.users[user_id] = {
            'id': user_id,
            'username': callback.from_user.username,
            'full_name': callback.from_user.full_name,
            'tickets': [],
            'blocked': False
        }
    
    user = db.users[user_id]
    
    if len(user['tickets']) >= Config.MAX_TICKETS_PER_USER:
        await callback.answer("❌ Превышено количество активных запросов!")
        return
    
    await state.set_state(UserStates.select_category)
    await callback.message.edit_text(
        "📝 Выберите категорию вопроса:",
        reply_markup=category_keyboard()
    )

def category_keyboard() -> InlineKeyboardMarkup:
    categories = ["💻 Техподдержка", "💰 Оплата", "📋 Другое"]
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat, callback_data=f"cat_{cat}")
    builder.adjust(2)
    return builder.as_markup()

@dp.callback_query(F.data.startswith("cat_"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    await callback.message.edit_text(
        "🚨 Выберите приоритет:",
        reply_markup=ticket_priority_kb()
    )
    await state.set_state(UserStates.create_ticket)

@dp.callback_query(F.data.in_({"urgent", "medium", "low"}))
async def set_priority(callback: CallbackQuery, state: FSMContext):
    await state.update_data(priority=callback.data)
    await callback.message.edit_text(
        "📝 Опишите вашу проблему максимально подробно:\n"
        "(Вы можете прикрепить файлы, фото или видео)"
    )
    await state.set_state(UserStates.create_ticket)

@dp.message(UserStates.create_ticket)
async def create_ticket_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = db.counters['ticket_id']
    
    attachments = []
    if message.content_type != ContentType.TEXT:
        file_id = None
        if message.content_type == ContentType.PHOTO:
            file_id = message.photo[-1].file_id
        elif message.content_type == ContentType.DOCUMENT:
            file_id = message.document.file_id
        elif message.content_type == ContentType.VIDEO:
            file_id = message.video.file_id
        
        attachments.append({
            'type': message.content_type,
            'file_id': file_id,
            'caption': message.caption
        })

    db.tickets[ticket_id] = {
        'id': ticket_id,
        'user_id': message.from_user.id,
        'category': data['category'],
        'priority': data['priority'],
        'status': TicketStatus.NEW,
        'messages': [{
            'text': message.html_text,
            'date': datetime.now(),
            'type': 'user',
            'attachments': attachments
        }],
        'created_at': datetime.now(),
        'closed_at': None
    }
    

    db.statistics['total_tickets'] += 1
    db.statistics['categories'][data['category']] += 1
    db.statistics['priorities'][data['priority']] += 1
    
    db.users[message.from_user.id]['tickets'].append(ticket_id)
    db.counters['ticket_id'] += 1
    
    await message.answer(
        f"✅ Запрос #{ticket_id} создан!\n"
        "Ожидайте ответа нашего специалиста.",
        reply_markup=main_menu(message.from_user.id)
    )
    
    await notify_admins(ticket_id)
    await state.clear()

async def notify_admins(ticket_id: int, update: bool = False):
    ticket = db.tickets[ticket_id]
    user = db.users[ticket['user_id']]
    
    text = (
        f"📮 {'Обновление' if update else 'Новый'} запрос #{ticket_id}\n"
        f"👤 Пользователь: {user['full_name']}\n"
        f"📋 Категория: {ticket['category']}\n"
        f"🚨 Приоритет: {ticket['priority']}\n"
        f"📝 Последнее сообщение: {ticket['messages'][-1]['text'][:200]}..."
    )
    
    for admin_id in Config.ADMIN_IDS:
        try:
            msg = await bot.send_message(
                admin_id,
                text,
                reply_markup=ticket_actions(ticket_id))
            ticket['admin_message_id'] = msg.message_id
        except Exception as e:
            logger.error(f"Admin {admin_id} notification failed: {e}")

@dp.callback_query(F.data.startswith("reply_"))
async def reply_ticket(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split("_")[1])
    await state.update_data(ticket_id=ticket_id)
    await state.set_state(AdminStates.answer_ticket)
    await callback.message.answer(
        f"💬 Введите ответ для запроса #{ticket_id}:")

@dp.message(AdminStates.answer_ticket)
async def process_admin_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = data['ticket_id']
    ticket = db.tickets[ticket_id]
    
    try:
        await bot.send_message(
            ticket['user_id'],
            f"📩 Ответ на ваш запрос #{ticket_id}:\n{message.html_text}",
            reply_markup=main_menu(ticket['user_id'])
        )
        ticket['status'] = TicketStatus.IN_PROGRESS
        ticket['messages'].append({
            'text': message.html_text,
            'date': datetime.now(),
            'type': 'support'
        })
        
        await message.answer(f"✅ Ответ отправлен для запроса #{ticket_id}")
        await update_ticket_message(ticket_id)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    
    await state.clear()

async def update_ticket_message(ticket_id: int):
    ticket = db.tickets[ticket_id]
    text = (
        f"📌 Запрос #{ticket_id}\n"
        f"Статус: {ticket['status']}\n"
        f"Обновлен: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.edit_message_text(
                text,
                chat_id=admin_id,
                message_id=ticket['admin_message_id'],
                reply_markup=ticket_actions(ticket_id)
            )
        except:
            pass

@dp.callback_query(F.data.startswith("close_"))
async def close_ticket(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[1])
    ticket = db.tickets[ticket_id]
    ticket['status'] = TicketStatus.CLOSED
    ticket['closed_at'] = datetime.now()
    
    await callback.answer("✅ Запрос закрыт")
    await update_ticket_message(ticket_id)
    await notify_user_about_close(ticket_id)

async def notify_user_about_close(ticket_id: int):
    ticket = db.tickets[ticket_id]
    await bot.send_message(
        ticket['user_id'],
        f"📭 Ваш запрос #{ticket_id} был закрыт.\n"
        "Если проблема не решена, создайте новый запрос.",
        reply_markup=main_menu(ticket['user_id'])
    )

async def check_overdue_tickets():
    while True:
        await asyncio.sleep(300)
        now = datetime.now()
        for ticket in db.tickets.values():
            if ticket['status'] == TicketStatus.NEW:
                if (now - ticket['created_at']).seconds > Config.REQUEST_TIMEOUT:
                    await notify_admins_about_overdue(ticket['id'])

async def notify_admins_about_overdue(ticket_id: int):
    for admin_id in Config.ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"🚨 Запрос #{ticket_id} требует внимания! Время ожидания превышено.",
            reply_markup=ticket_actions(ticket_id)
        )

@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if callback.from_user.id not in Config.ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещен!")
        return
    
    text = (
        "🛠 Панель администратора\n"
        f"• Активных запросов: {len([t for t in db.tickets.values() if t['status'] != TicketStatus.CLOSED])}\n"
        f"• Новых: {len([t for t in db.tickets.values() if t['status'] == TicketStatus.NEW])}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
             InlineKeyboardButton(text="📋 Все запросы", callback_data="all_tickets")]
        ])
    )

@dp.callback_query(F.data == "my_tickets")
async def show_user_tickets(callback: CallbackQuery):
    user = db.users.get(callback.from_user.id)
    if not user or not user['tickets']:
        await callback.answer("У вас нет активных запросов!")
        return
    
    active_tickets = [t for t in user['tickets'] if db.tickets[t]['status'] != TicketStatus.CLOSED]
    closed_tickets = [t for t in user['tickets'] if db.tickets[t]['status'] == TicketStatus.CLOSED]
    
    text = (
        f"📂 Ваши запросы:\n"
        f"• Активные: {len(active_tickets)}\n"
        f"• Закрытые: {len(closed_tickets)}\n\n"
        "Выберите запрос для просмотра:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=tickets_list_kb(user['tickets'])
    )

@dp.callback_query(F.data.startswith("view_ticket_"))
async def view_ticket_details(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[-1])
    ticket = db.tickets.get(ticket_id)
    
    if not ticket:
        await callback.answer("Запрос не найден!")
        return
    
    text = (
        f"📄 Запрос #{ticket_id}\n"
        f"Статус: {ticket['status']}\n"
        f"Категория: {ticket['category']}\n"
        f"Приоритет: {ticket['priority']}\n"
        f"Дата создания: {ticket['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
        f"Сообщений: {len(ticket['messages'])}\n\n"
        f"Последнее сообщение:\n{ticket['messages'][-1]['text'][:300]}..."
    )
    
    markup = InlineKeyboardBuilder()
    if ticket['status'] != TicketStatus.CLOSED:
        markup.button(text="✉️ Добавить комментарий", callback_data=f"add_comment_{ticket_id}")
    # markup.button(text="🔙 Назад", callback_data="my_tickets")

        markup.button(text="📨 Новый запрос", callback_data="new_ticket")
        markup.button(text="📂 Мои запросы", callback_data="my_tickets")
        markup.adjust(1)
        return markup.as_markup()




    await callback.message.edit_text(
        text,
        reply_markup=markup.as_markup()
    )

@dp.callback_query(F.data.startswith("add_comment_"))
async def add_comment_to_ticket(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split("_")[-1])
    await state.update_data(ticket_id=ticket_id)
    await state.set_state(UserStates.add_comment)
    await callback.message.answer("Введите ваш комментарий:")

@dp.message(UserStates.add_comment)
async def process_user_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = data['ticket_id']
    
    db.tickets[ticket_id]['messages'].append({
        'text': message.html_text,
        'date': datetime.now(),
        'type': 'user'
    })
    
    await message.answer("✅ Комментарий добавлен!")
    await state.clear()
    await notify_admins(ticket_id, update=True)

@dp.callback_query(F.data == "stats")
async def show_statistics(callback: CallbackQuery):
    stats = db.statistics
    avg_time = "N/A"
    if stats['response_times']:
        avg_seconds = sum(stats['response_times']) / len(stats['response_times'])
        avg_time = str(timedelta(seconds=int(avg_seconds)))
    
    text = (
        "📊 Статистика системы:\n"
        f"• Всего запросов: {stats['total_tickets']}\n"
        f"• Среднее время ответа: {avg_time}\n"
        "📋 По категориям:\n" + 
        "\n".join([f" - {k}: {v}" for k, v in stats['categories'].items()]) +
        "\n\n🚨 По приоритетам:\n" +
        "\n".join([f" - {k}: {v}" for k, v in stats['priorities'].items()])
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
        ])
    )

@dp.callback_query(F.data == "all_tickets")
async def show_all_tickets(callback: CallbackQuery):
    open_tickets = [t for t in db.tickets.values() if t['status'] != TicketStatus.CLOSED]
    
    text = (
        "📋 Все активные запросы:\n"
        f"• Всего: {len(open_tickets)}\n"
        f"• Срочных: {len([t for t in open_tickets if t['priority'] == 'urgent'])}\n"
        "Список запросов:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=tickets_list_kb(
            [t['id'] for t in sorted(open_tickets, key=lambda x: x['created_at'], reverse=True)],
            items_per_page=8
        )
    )

@dp.errors()
async def error_handler(event: types.ErrorEvent):
    logger.error(f"Error: {event.exception}", exc_info=True)

async def main():
    await bot.delete_webhook()
    asyncio.create_task(check_overdue_tickets())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("Starting support bot...")
    asyncio.run(main())