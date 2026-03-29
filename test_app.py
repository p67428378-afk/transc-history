import pytest
from app import app
from datetime import datetime, timedelta
import json

@pytest.fixture
def client():
    """
    Configures the Flask test client.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_transactions_no_filters(client):
    """
    Tests retrieving transactions without any filters.
    Expects a 200 OK response with a list of transactions.
    """
    response = client.get('/transactions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "transaction_id" in data[0]
    assert "amount" in data[0]

def test_get_transactions_date_filter(client):
    """
    Tests filtering transactions by a specific date range.
    """
    today = datetime.now()
    one_month_ago = today - timedelta(days=30)
    start_date_str = one_month_ago.strftime('%Y-%m-%d')
    end_date_str = today.strftime('%Y-%m-%d')

    response = client.get(f'/transactions?start_date={start_date_str}&end_date={end_date_str}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    for transaction in data:
        tx_date = datetime.strptime(transaction['transaction_date'], '%Y-%m-%d')
        assert one_month_ago.date() <= tx_date.date() <= today.date()

def test_get_transactions_type_filter(client):
    """
    Tests filtering transactions by type (credit).
    """
    response = client.get('/transactions?transaction_type=credit')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    for transaction in data:
        assert transaction['transaction_type'] == 'credit'

def test_get_transactions_amount_filter(client):
    """
    Tests filtering transactions by amount range.
    """
    min_amount = 100.00
    max_amount = 500.00
    response = client.get(f'/transactions?min_amount={min_amount}&max_amount={max_amount}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    for transaction in data:
        assert min_amount <= transaction['amount'] <= max_amount

def test_get_transactions_invalid_date_range(client):
    """
    Tests invalid date range (start_date after end_date).
    """
    response = client.get('/transactions?start_date=2024-01-01&end_date=2023-01-01')
    assert response.status_code == 400
    assert "Invalid date range" in json.loads(response.data)['error']

def test_get_transactions_invalid_amount_range(client):
    """
    Tests invalid amount range (min_amount greater than max_amount).
    """
    response = client.get('/transactions?min_amount=500&max_amount=100')
    assert response.status_code == 400
    assert "Invalid amount range" in json.loads(response.data)['error']

def test_get_transactions_negative_amount(client):
    """
    Tests negative amount input.
    """
    response = client.get('/transactions?min_amount=-100')
    assert response.status_code == 400
    assert "Invalid amount: min_amount cannot be negative" in json.loads(response.data)['error']

def test_get_transactions_no_results(client):
    """
    Tests a filter combination that yields no results.
    """
    # Assuming no transactions will be exactly this amount
    response = client.get('/transactions?min_amount=999999.00&max_amount=1000000.00')
    assert response.status_code == 404
    assert "No transactions found" in json.loads(response.data)['message']

def test_download_pdf_no_filters(client):
    """
    Tests downloading PDF without filters.
    """
    response = client.get('/transactions/download_pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=transaction_statement.pdf')
    assert len(response.data) > 1000 # PDF should have some content

def test_download_pdf_with_filters(client):
    """
    Tests downloading PDF with date and type filters.
    """
    today = datetime.now()
    six_months_ago = today - timedelta(days=180)
    start_date_str = six_months_ago.strftime('%Y-%m-%d')
    end_date_str = today.strftime('%Y-%m-%d')

    response = client.get(f'/transactions/download_pdf?start_date={start_date_str}&end_date={end_date_str}&transaction_type=debit')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=transaction_statement.pdf')
    assert len(response.data) > 1000 # PDF should have some content

def test_download_pdf_no_results(client):
    """
    Tests downloading PDF when no transactions match filters.
    The PDF should still be generated but indicate no transactions.
    """
    response = client.get('/transactions/download_pdf?min_amount=999999.00&max_amount=1000000.00')
    assert response.status_code == 200 # Still returns 200, but PDF content will state no transactions
    assert response.mimetype == 'application/pdf'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=transaction_statement.pdf')
    # We can't easily check PDF content here without a PDF parser,
    # but the generate_transaction_pdf function handles this case.
