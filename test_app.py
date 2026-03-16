import pytest
from app import app, mock_transactions, generate_pdf_statement
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_transactions_success(client):
    # Test with a valid customer_id and default date range (last 12 months)
    response = client.get("/transactions?customer_id=123")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    for transaction in data:
        assert transaction["customer_id"] == "123"
        t_date = datetime.strptime(transaction["transaction_date"], "%Y-%m-%d")
        assert t_date >= (datetime.now() - relativedelta(months=12) - timedelta(days=1)) # Allow for slight day difference
        assert t_date <= datetime.now()

def test_get_transactions_no_customer_id(client):
    response = client.get("/transactions")
    assert response.status_code == 400
    assert response.get_json() == {"message": "customer_id is required"}

def test_get_transactions_invalid_date_format(client):
    response = client.get("/transactions?customer_id=123&start_date=2023-XX-01")
    assert response.status_code == 400
    assert response.get_json() == {"message": "Invalid start_date format. Use YYYY-MM-DD"}

def test_get_transactions_start_date_after_end_date(client):
    response = client.get("/transactions?customer_id=123&start_date=2024-03-01&end_date=2024-02-01")
    assert response.status_code == 400
    assert response.get_json() == {"message": "start_date cannot be after end_date"}

def test_get_transactions_end_date_in_future(client):
    future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    response = client.get(f"/transactions?customer_id=123&end_date={future_date}")
    assert response.status_code == 400
    assert response.get_json() == {"message": "end_date cannot be in the future"}

def test_get_transactions_filter_by_date_range(client):
    response = client.get("/transactions?customer_id=123&start_date=2023-01-01&end_date=2023-02-28")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2  # T001, T003
    for transaction in data:
        t_date = datetime.strptime(transaction["transaction_date"], "%Y-%m-%d")
        assert datetime(2023, 1, 1) <= t_date <= datetime(2023, 2, 28)

def test_get_transactions_filter_by_type(client):
    response = client.get("/transactions?customer_id=123&type=credit")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    for transaction in data:
        assert transaction["transaction_type"] == "credit"

def test_get_transactions_filter_by_amount_range(client):
    response = client.get("/transactions?customer_id=123&min_amount=100&max_amount=300")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    for transaction in data:
        assert 100 <= transaction["amount"] <= 300

def test_get_transactions_no_results(client):
    response = client.get("/transactions?customer_id=999") # Non-existent customer
    assert response.status_code == 200 # Should return 200 with empty message
    assert response.get_json() == {"message": "No transactions found for the selected criteria."} 

def test_download_pdf_success(client):
    response = client.get("/transactions/download?customer_id=123&start_date=2023-01-01&end_date=2024-03-01")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment" in response.headers["Content-Disposition"]
    assert len(response.data) > 0

def test_download_pdf_no_transactions(client):
    response = client.get("/transactions/download?customer_id=999")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment" in response.headers["Content-Disposition"]
    assert b"No transactions found for the selected criteria." in response.data

def test_download_pdf_missing_customer_id(client):
    response = client.get("/transactions/download")
    assert response.status_code == 400
    assert response.get_json() == {"message": "customer_id is required"}

def test_generate_pdf_statement_empty_transactions():
    pdf_buffer = generate_pdf_statement([])
    content = pdf_buffer.getvalue()
    assert b"No transactions found for the selected criteria." in content

def test_generate_pdf_statement_with_transactions():
    sample_transactions = [
        {
            "transaction_id": "T001",
            "customer_id": "123",
            "account_number": "ACC001",
            "transaction_date": "2023-01-15",
            "transaction_type": "credit",
            "amount": 100.00,
            "currency": "USD",
            "description": "Salary Deposit",
            "merchant_info": "Employer Inc.",
        }
    ]
    pdf_buffer = generate_pdf_statement(sample_transactions)
    content = pdf_buffer.getvalue()
    assert b"Salary Deposit" in content
    assert b"Amount: USD 100.00" in content
