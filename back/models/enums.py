from enum import Enum

class AdStatus(str, Enum):
    PENDING_MODERATION = "Pending Moderation"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    REJECTED = "Rejected"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    FEE = "fee"             # Комиссия
    REFERRAL = "referral"   # Реферальные

class TransactionCurrencyType(str, Enum):
    TON = "TON"
    BTC = "BTC"
    USDT = "USDT"
    JET = "JET" 

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
