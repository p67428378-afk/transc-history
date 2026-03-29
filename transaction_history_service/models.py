from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

Base = declarative_base()

class TransactionType(enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(Integer, primary_key=True)
    account_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="customer")

    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, name='{self.name}')>"

class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True)
    account_number = Column(String, ForeignKey('customers.account_number'), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default='USD', nullable=False)
    description = Column(String)
    merchant_info = Column(String)

    customer = relationship("Customer", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, amount={self.amount}, type='{self.transaction_type.value}')>"
