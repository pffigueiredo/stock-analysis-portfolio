from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum


class AlertType(str, Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_CHANGE = "percent_change"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    full_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    portfolios: List["Portfolio"] = Relationship(back_populates="user")
    price_alerts: List["PriceAlert"] = Relationship(back_populates="user")


class Stock(SQLModel, table=True):
    __tablename__ = "stocks"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(max_length=10, unique=True, index=True)
    name: str = Field(max_length=200)
    exchange: str = Field(max_length=50)
    sector: str = Field(max_length=100, default="")
    industry: str = Field(max_length=100, default="")
    market_cap: Optional[Decimal] = Field(default=None, decimal_places=2)
    current_price: Decimal = Field(decimal_places=4, default=Decimal("0"))
    previous_close: Decimal = Field(decimal_places=4, default=Decimal("0"))
    day_change: Decimal = Field(decimal_places=4, default=Decimal("0"))
    day_change_percent: Decimal = Field(decimal_places=4, default=Decimal("0"))
    volume: int = Field(default=0)
    avg_volume: int = Field(default=0)
    pe_ratio: Optional[Decimal] = Field(default=None, decimal_places=2)
    dividend_yield: Optional[Decimal] = Field(default=None, decimal_places=4)
    fifty_two_week_high: Optional[Decimal] = Field(default=None, decimal_places=4)
    fifty_two_week_low: Optional[Decimal] = Field(default=None, decimal_places=4)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    portfolio_holdings: List["PortfolioHolding"] = Relationship(back_populates="stock")
    price_history: List["StockPriceHistory"] = Relationship(back_populates="stock")
    price_alerts: List["PriceAlert"] = Relationship(back_populates="stock")


class Portfolio(SQLModel, table=True):
    __tablename__ = "portfolios"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(max_length=500, default="")
    user_id: int = Field(foreign_key="users.id")
    total_value: Decimal = Field(decimal_places=2, default=Decimal("0"))
    total_cost: Decimal = Field(decimal_places=2, default=Decimal("0"))
    total_gain_loss: Decimal = Field(decimal_places=2, default=Decimal("0"))
    total_gain_loss_percent: Decimal = Field(decimal_places=4, default=Decimal("0"))
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="portfolios")
    holdings: List["PortfolioHolding"] = Relationship(back_populates="portfolio")


class PortfolioHolding(SQLModel, table=True):
    __tablename__ = "portfolio_holdings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolios.id")
    stock_id: int = Field(foreign_key="stocks.id")
    quantity: Decimal = Field(decimal_places=8, default=Decimal("0"))
    average_cost: Decimal = Field(decimal_places=4, default=Decimal("0"))
    total_cost: Decimal = Field(decimal_places=2, default=Decimal("0"))
    current_value: Decimal = Field(decimal_places=2, default=Decimal("0"))
    gain_loss: Decimal = Field(decimal_places=2, default=Decimal("0"))
    gain_loss_percent: Decimal = Field(decimal_places=4, default=Decimal("0"))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    portfolio: Portfolio = Relationship(back_populates="holdings")
    stock: Stock = Relationship(back_populates="portfolio_holdings")
    transactions: List["Transaction"] = Relationship(back_populates="holding")


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    holding_id: int = Field(foreign_key="portfolio_holdings.id")
    transaction_type: str = Field(max_length=10)  # 'BUY' or 'SELL'
    quantity: Decimal = Field(decimal_places=8)
    price: Decimal = Field(decimal_places=4)
    total_amount: Decimal = Field(decimal_places=2)
    fees: Decimal = Field(decimal_places=2, default=Decimal("0"))
    notes: str = Field(max_length=500, default="")
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    holding: PortfolioHolding = Relationship(back_populates="transactions")


class StockPriceHistory(SQLModel, table=True):
    __tablename__ = "stock_price_history"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="stocks.id")
    date: datetime = Field(index=True)
    open_price: Decimal = Field(decimal_places=4)
    high_price: Decimal = Field(decimal_places=4)
    low_price: Decimal = Field(decimal_places=4)
    close_price: Decimal = Field(decimal_places=4)
    volume: int = Field(default=0)
    adjusted_close: Optional[Decimal] = Field(default=None, decimal_places=4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stock: Stock = Relationship(back_populates="price_history")


class PriceAlert(SQLModel, table=True):
    __tablename__ = "price_alerts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    stock_id: int = Field(foreign_key="stocks.id")
    alert_type: AlertType = Field(default=AlertType.PRICE_ABOVE)
    target_price: Optional[Decimal] = Field(default=None, decimal_places=4)
    target_percentage: Optional[Decimal] = Field(default=None, decimal_places=2)
    status: AlertStatus = Field(default=AlertStatus.ACTIVE)
    message: str = Field(max_length=500, default="")
    triggered_at: Optional[datetime] = Field(default=None)
    triggered_price: Optional[Decimal] = Field(default=None, decimal_places=4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="price_alerts")
    stock: Stock = Relationship(back_populates="price_alerts")


class WatchList(SQLModel, table=True):
    __tablename__ = "watch_lists"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100)
    description: str = Field(max_length=500, default="")
    stock_symbols: List[str] = Field(default=[], sa_column=Column(JSON))
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MarketIndex(SQLModel, table=True):
    __tablename__ = "market_indices"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(max_length=10, unique=True)
    name: str = Field(max_length=100)
    current_value: Decimal = Field(decimal_places=4, default=Decimal("0"))
    previous_close: Decimal = Field(decimal_places=4, default=Decimal("0"))
    day_change: Decimal = Field(decimal_places=4, default=Decimal("0"))
    day_change_percent: Decimal = Field(decimal_places=4, default=Decimal("0"))
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    full_name: str = Field(max_length=100)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class StockCreate(SQLModel, table=False):
    symbol: str = Field(max_length=10)
    name: str = Field(max_length=200)
    exchange: str = Field(max_length=50)
    sector: str = Field(max_length=100, default="")
    industry: str = Field(max_length=100, default="")


class StockUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    sector: Optional[str] = Field(default=None, max_length=100)
    industry: Optional[str] = Field(default=None, max_length=100)
    current_price: Optional[Decimal] = Field(default=None, decimal_places=4)
    market_cap: Optional[Decimal] = Field(default=None, decimal_places=2)


class PortfolioCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: str = Field(max_length=500, default="")
    user_id: int
    is_default: bool = Field(default=False)


class PortfolioUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_default: Optional[bool] = Field(default=None)


class TransactionCreate(SQLModel, table=False):
    holding_id: int
    transaction_type: str = Field(max_length=10)
    quantity: Decimal = Field(decimal_places=8)
    price: Decimal = Field(decimal_places=4)
    fees: Decimal = Field(decimal_places=2, default=Decimal("0"))
    notes: str = Field(max_length=500, default="")
    transaction_date: Optional[datetime] = Field(default=None)


class PriceAlertCreate(SQLModel, table=False):
    user_id: int
    stock_id: int
    alert_type: AlertType = Field(default=AlertType.PRICE_ABOVE)
    target_price: Optional[Decimal] = Field(default=None, decimal_places=4)
    target_percentage: Optional[Decimal] = Field(default=None, decimal_places=2)
    message: str = Field(max_length=500, default="")


class PriceAlertUpdate(SQLModel, table=False):
    alert_type: Optional[AlertType] = Field(default=None)
    target_price: Optional[Decimal] = Field(default=None, decimal_places=4)
    target_percentage: Optional[Decimal] = Field(default=None, decimal_places=2)
    status: Optional[AlertStatus] = Field(default=None)
    message: Optional[str] = Field(default=None, max_length=500)


class WatchListCreate(SQLModel, table=False):
    user_id: int
    name: str = Field(max_length=100)
    description: str = Field(max_length=500, default="")
    stock_symbols: List[str] = Field(default=[])
    is_default: bool = Field(default=False)


class WatchListUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    stock_symbols: Optional[List[str]] = Field(default=None)
    is_default: Optional[bool] = Field(default=None)


class StockPriceHistoryCreate(SQLModel, table=False):
    stock_id: int
    date: datetime
    open_price: Decimal = Field(decimal_places=4)
    high_price: Decimal = Field(decimal_places=4)
    low_price: Decimal = Field(decimal_places=4)
    close_price: Decimal = Field(decimal_places=4)
    volume: int = Field(default=0)
    adjusted_close: Optional[Decimal] = Field(default=None, decimal_places=4)


class PortfolioSummary(SQLModel, table=False):
    portfolio_id: int
    portfolio_name: str
    total_value: Decimal
    total_cost: Decimal
    total_gain_loss: Decimal
    total_gain_loss_percent: Decimal
    holdings_count: int
    top_performers: List[Dict[str, Any]] = Field(default=[])
    worst_performers: List[Dict[str, Any]] = Field(default=[])


class StockQuote(SQLModel, table=False):
    symbol: str
    name: str
    current_price: Decimal
    day_change: Decimal
    day_change_percent: Decimal
    volume: int
    market_cap: Optional[Decimal] = Field(default=None)
    pe_ratio: Optional[Decimal] = Field(default=None)
    last_updated: datetime
