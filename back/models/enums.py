from enum import Enum

class AdStatus(str, Enum):
    PENDING_MODERATION = "PENDING_MODERATION"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    FEE = "fee"
    REFERRAL = "referral"

class TransactionCurrencyType(str, Enum):
    TON = "TON"
    USDT = "USDT"
    # BTC = "BTC"
    # ETH = "ETH"

class TransactionStatus(str, Enum):
    PENDING = "Pending"
    SUCCESSFUL = "Successful"
    CANCELLED = "Cancelled"

class DealStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    FROZEN = "Frozen"

class CategoriesAds(str, Enum):
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

class TypeUserAcquisition(str, Enum):
    # NATIVE = "Нативный"
    BOT_NEWSLETTER = "Рассылка в боте"
    POST = "Пост в каналах"
    MOTIVE = "Мотив"

class PrizeType(str, Enum):
    DISCOUNT_5 = "5%_discount" # скидка на размещение (платное) работает 1 раз
    DEPOSIT_3 = "3%_deposit" # + 3% к депозиту (до 1000$)
    LOWER_COMMISSION_20 = "lower_commission_20%" # -20% на вывод средств 
    DISCOUNT_10 = "10%_discount" # скидка на размещение (платное) работает 1 раз
