from enum import Enum

class AdStatus(str, Enum):
    PENDING_MODERATION = "Pending Moderation"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    REJECTED = "Rejected"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"     # Пополнение
    WITHDRAWAL = "withdrawal" # Вывод
    FEE = "fee"             # Комиссия
    REFERRAL = "referral"   # Реферальные

class TransactionCurrencyType(str, Enum):
    TON = "TON"
    BTC = "BTC"
    USDT = "USDT"
    JET = "JET" 
    
    @property
    def label_en(self):
        return self.value

    @property
    def label_ru(self):
        labels = {
            "USDT": "Тезер",
            "TON": "Тонкойн",
            "NOT": "Ноткоин",
            "BITCOIN": "Биткойн",
            "SOLANA": "Солана"
        }
        return labels.get(self.name, self.name) 

class TransactionStatus(str, Enum):
    PENDING = "Pending"
    SUCCESSFUL = "Successful"
    CANCELLED = "Cancelled"

class DealStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FROZEN = "Frozen"

class Categories(str, Enum):
    GAMES = "Games"
    CRYPTOCURRENCY = "Cryptocurrency"
    EDUCATIONAL = "Educational"
    STREAMERS = "Streamers"
    TRADING = "Trading"
    INVESTMENTS = "Investments"
    HUMOR = "Humor"
    FREEBIES = "Freebies"
    JOB_SEARCH = "Job Search"
    BLOG = "Blog"
    ADAPTERS = "Adapters"
    GAMBLING = "Gambling"
    ART = "Art"
    TAPALKS = "Tapalki"
    TRASH = "Trash"
    OTHER = "Other"    

    @property
    def label_en(self):
        return self.value

    @property
    def label_ru(self):
        labels = {
            "GAMES": "Игры",
            "CRYPTOCURRENCY": "Криптовалюта",
            "OTHER": "Другое",
            "EDUCATIONAL": "Познавательная",
            "STREAMERS": "Строчники",
            "TRADING": "Трейдинг",
            "INVESTMENTS": "Инвестиции",
            "HUMOR": "Юмор",
            "FREEBIES": "Халява",
            "JOB_SEARCH": "Поиск работы",
            "BLOG": "Блог",
            "ADAPTERS": "Переходники",
            "GAMBLING": "Гемблинг",
            "ART": "Искусство",
            "TAPALKS": "Тапалки",
            "TRASH": "Треш"
        }
        return labels.get(self.name, self.name)

