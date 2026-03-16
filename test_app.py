import pytest
from app import app, db, Transaction, generate_dummy_transactions
from datetime import datetime, timedelta
import io

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Generate a small, predictable set of dummy transactions for testing
            # Clear existing transactions first to ensure a clean state
            db.session.query(Transaction).delete()
            db.session.commit()

            # Add specific transactions for testing
            today = datetime.utcnow()
            db.session.add(Transaction(account_number='TEST001', transaction_date=today - timedelta(days=10), transaction_type='credit', amount=100.00, description='Test Credit 1'))
            db.session.add(Transaction(account_number='TEST001', transaction_date=today - timedelta(days=20), transaction_type='debit', amount=50.00, description='Test Debit 1'))
            db.session.add(Transaction(account_number='TEST001', transaction_date=today - timedelta(days=30), transaction_type='credit', amount=200.00, description='Test Credit 2'))
            db.session.add(Transaction(account_number='TEST002', transaction_date=today - timedelta(days=5), transaction_type='debit', amount=75.00, description='Other Account Debit'))
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_get_transactions_no_filters(client):
    response = client.get('/transactions?account_number=TEST001')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3  # Should get all 3 transactions for TEST001
    assert data[0]['transaction_type'] == 'credit' # Ordered by date desc

def test_get_transactions_filter_by_type(client):
    response = client.get('/transactions?account_number=TEST001&type=credit')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    for t in data:
        assert t['transaction_type'] == 'credit'

def test_get_transactions_filter_by_date_range(client):
    today = datetime.utcnow()
    start_date = (today - timedelta(days=25)).strftime('%Y-%m-%d')
    end_date = (today - timedelta(days=15)).strftime('%Y-%m-%d')
    response = client.get(f'/transactions?account_number=TEST001&start_date={start_date}&end_date={end_date}')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['transaction_type'] == 'debit'
    assert data[0]['amount'] == 50.00

def test_get_transactions_filter_by_amount_range(client):
    response = client.get('/transactions?account_number=TEST001&min_amount=150&max_amount=250')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['amount'] == 200.00

def test_get_transactions_no_results(client):
    response = client.get('/transactions?account_number=TEST001&type=debit&min_amount=1000')
    assert response.status_code == 404
    assert response.get_json() == {'message': 'No transactions found for the selected criteria.'}

def test_download_pdf_success(client):
    response = client.get('/transactions/download-pdf?account_number=TEST001')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    assert 'attachment; filename=transaction_statement.pdf' in response.headers['Content-Disposition']
    assert len(response.data) > 0 # PDF content should not be empty

def test_download_pdf_no_transactions(client):
    response = client.get('/transactions/download-pdf?account_number=TEST001&type=debit&min_amount=1000')
    assert response.status_code == 200 # Should return a PDF indicating no data
    assert response.headers['Content-Type'] == 'application/pdf'
    assert 'attachment; filename=transaction_statement_no_data.pdf' in response.headers['Content-Disposition']
    assert len(response.data) > 0
    # Further checks could involve parsing the PDF content, but for a basic test, size check is sufficient.

def test_invalid_date_format(client):
    response = client.get('/transactions?account_number=TEST001&start_date=2023/01/01')
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid date format. Use YYYY-MM-DD.'}

def test_start_date_after_end_date(client):
    today = datetime.utcnow().strftime('%Y-%m-%d')
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    response = client.get(f'/transactions?account_number=TEST001&start_date={today}&end_date={yesterday}')
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Start date cannot be after end date.'}

def test_invalid_transaction_type(client):
    response = client.get('/transactions?account_number=TEST001&type=invalid_type')
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid transaction type. Use "credit" or "debit".'}

def test_negative_min_amount(client):
    response = client.get('/transactions?account_number=TEST001&min_amount=-10')
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Minimum amount cannot be negative.'}

def test_negative_max_amount(client):
    response = client.get('/transactions?account_number=TEST001&max_amount=-10')
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Maximum amount cannot be negative.'}
