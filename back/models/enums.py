from enum import Enum

class AdStatus(str, Enum):
    PENDING_MODERATION = "Pending Moderation"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    REJECTED = "Rejected"

class TransactionType(str, Enum):
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"

class TransactionCurrencyType(str, Enum):
    USDT = "Tether"
    TON = "Toncoin"
    NOT = "Notcoin"
    BITCOIN = "Bitcoin"
    SOLANA = "Solana"

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
    OTHER = "Other"
