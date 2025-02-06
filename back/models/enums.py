from enum import Enum

class AdStatus(str, Enum):
    PENDING_MODERATION = "PENDING_MODERATION"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    FEE = "fee"             # Комиссия
    REFERRAL = "referral"   # Реферальные

class TransactionCurrencyType(str, Enum):
    TON = "TON"
    BTC = "BTC"
    USDT = "USDT"
    ETH = "ETH" 

class TransactionStatus(str, Enum):
    PENDING = "Pending"
    SUCCESSFUL = "Successful"
    CANCELLED = "Cancelled"

class DealStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
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

class TypeUserAcquisition(str, Enum): # Тип привлечения пользователей
    POST = "Post"
    BOT_NEWSLETTER = "Рассылка в боте"
    GIVEAEAY_TG_CHANNEL = "Розыгрыш"
