from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(50), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'credit' or 'debit'
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    description = db.Column(db.String(200), nullable=True)
    merchant_info = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Transaction {self.transaction_id} - {self.account_number}>"

    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'account_number': self.account_number,
            'transaction_date': self.transaction_date.isoformat(),
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'currency': self.currency,
            'description': self.description,
            'merchant_info': self.merchant_info
        }
