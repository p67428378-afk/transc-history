from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()

def generate_dummy_transactions(num_transactions: int = 100, account_number: str = "1234567890") -> list:
    """
    Generates a list of dummy transaction records.

    Args:
        num_transactions (int): The number of dummy transactions to generate.
        account_number (str): The account number to associate with the transactions.

    Returns:
        list: A list of dictionaries, each representing a transaction.
    """
    transactions = []
    for _ in range(num_transactions):
        transaction_date = fake.date_time_between(start_date="-13M", end_date="now")
        transaction_type = random.choice(['credit', 'debit'])
        amount = round(random.uniform(5.00, 1000.00), 2)
        description = fake.sentence(nb_words=6)

        transactions.append({
            "transaction_id": fake.uuid4(),
            "account_number": account_number,
            "transaction_date": transaction_date,
            "transaction_type": transaction_type,
            "amount": amount,
            "currency": "USD",
            "description": description
        })
    return transactions

# Generate a static set of dummy transactions for consistency
_ALL_TRANSACTIONS = generate_dummy_transactions(num_transactions=500)

def get_transactions_data(
    start_date: datetime = None,
    end_date: datetime = None,
    transaction_type: str = None,
    min_amount: float = None,
    max_amount: float = None
) -> list:
    """
    Retrieves and filters transaction data.

    Args:
        start_date (datetime, optional): Start date for filtering. Defaults to 12 months ago.
        end_date (datetime, optional): End date for filtering. Defaults to now.
        transaction_type (str, optional): Filter by 'credit' or 'debit'.
        min_amount (float, optional): Minimum transaction amount.
        max_amount (float, optional): Maximum transaction amount.

    Returns:
        list: A list of filtered transaction dictionaries.
    """
    filtered_transactions = []

    # Default date range to last 12 months if not provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=365)

    for transaction in _ALL_TRANSACTIONS:
        tx_date = transaction['transaction_date']
        tx_type = transaction['transaction_type']
        tx_amount = transaction['amount']

        # Apply date filter
        if not (start_date <= tx_date <= end_date):
            continue

        # Apply transaction type filter
        if transaction_type and tx_type != transaction_type.lower():
            continue

        # Apply amount filter
        if min_amount is not None and tx_amount < min_amount:
            continue
        if max_amount is not None and tx_amount > max_amount:
            continue

        filtered_transactions.append(transaction)

    # Sort by date in descending order
    filtered_transactions.sort(key=lambda x: x['transaction_date'], reverse=True)

    return filtered_transactions
