from flask import Flask, request, jsonify, send_file, Response
from datetime import datetime, timedelta
import io
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config.from_object('config.Config')

# Dummy Data - In a real application, this would come from a database
dummy_transactions = [
    {
        "transaction_id": "T001",
        "account_number": "ACC001",
        "transaction_date": "2023-01-15",
        "transaction_type": "credit",
        "amount": 200.00,
        "currency": "USD",
        "description": "Salary Deposit",
        "merchant_info": "Employer Inc.",
    },
    {
        "transaction_id": "T002",
        "account_number": "ACC001",
        "transaction_date": "2023-01-16",
        "transaction_type": "debit",
        "amount": 50.00,
        "currency": "USD",
        "description": "Groceries",
        "merchant_info": "SuperMart",
    },
    {
        "transaction_id": "T003",
        "account_number": "ACC001",
        "transaction_date": "2023-02-01",
        "transaction_type": "credit",
        "amount": 1000.00,
        "currency": "USD",
        "description": "Bonus",
        "merchant_info": "Employer Inc.",
    },
    {
        "transaction_id": "T004",
        "account_number": "ACC002",
        "transaction_date": "2023-02-05",
        "transaction_type": "debit",
        "amount": 25.00,
        "currency": "USD",
        "description": "Coffee",
        "merchant_info": "Cafe XYZ",
    },
    {
        "transaction_id": "T005",
        "account_number": "ACC001",
        "transaction_date": "2023-03-10",
        "transaction_type": "debit",
        "amount": 150.00,
        "currency": "USD",
        "description": "Utility Bill",
        "merchant_info": "PowerCo",
    },
    {
        "transaction_id": "T006",
        "account_number": "ACC001",
        "transaction_date": "2023-04-20",
        "transaction_type": "credit",
        "amount": 300.00,
        "currency": "USD",
        "description": "Freelance Payment",
        "merchant_info": "Client A",
    },
    {
        "transaction_id": "T007",
        "account_number": "ACC001",
        "transaction_date": "2023-05-01",
        "transaction_type": "debit",
        "amount": 75.00,
        "currency": "USD",
        "description": "Internet Bill",
        "merchant_info": "ISP Corp",
    },
    {
        "transaction_id": "T008",
        "account_number": "ACC001",
        "transaction_date": "2023-06-15",
        "transaction_type": "credit",
        "amount": 250.00,
        "currency": "USD",
        "description": "Refund",
        "merchant_info": "Retailer B",
    },
    {
        "transaction_id": "T009",
        "account_number": "ACC001",
        "transaction_date": "2023-07-01",
        "transaction_type": "debit",
        "amount": 120.00,
        "currency": "USD",
        "description": "Rent",
        "merchant_info": "Landlord LLC",
    },
    {
        "transaction_id": "T010",
        "account_number": "ACC001",
        "transaction_date": "2023-08-10",
        "transaction_type": "credit",
        "amount": 500.00,
        "currency": "USD",
        "description": "Investment Dividend",
        "merchant_info": "Investments Co.",
    },
    {
        "transaction_id": "T011",
        "account_number": "ACC001",
        "transaction_date": "2023-09-05",
        "transaction_type": "debit",
        "amount": 30.00,
        "currency": "USD",
        "description": "Subscription",
        "merchant_info": "Streaming Service",
    },
    {
        "transaction_id": "T012",
        "account_number": "ACC001",
        "transaction_date": "2023-10-20",
        "transaction_type": "credit",
        "amount": 150.00,
        "currency": "USD",
        "description": "Gift",
        "merchant_info": "Friend",
    },
    {
        "transaction_id": "T013",
        "account_number": "ACC001",
        "transaction_date": "2023-11-11",
        "transaction_type": "debit",
        "amount": 80.00,
        "currency": "USD",
        "description": "Dinner",
        "merchant_info": "Restaurant X",
    },
    {
        "transaction_id": "T014",
        "account_number": "ACC001",
        "transaction_date": "2023-12-01",
        "transaction_type": "credit",
        "amount": 2000.00,
        "currency": "USD",
        "description": "Year-end Bonus",
        "merchant_info": "Employer Inc.",
    },
    {
        "transaction_id": "T015",
        "account_number": "ACC001",
        "transaction_date": "2024-01-05",
        "transaction_type": "debit",
        "amount": 60.00,
        "currency": "USD",
        "description": "Books",
        "merchant_info": "Bookstore",
    },
]

def get_filtered_transactions():
    # Default to last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Parse query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    transaction_type = request.args.get('type')
    min_amount_str = request.args.get('min_amount')
    max_amount_str = request.args.get('max_amount')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return {"message": "Invalid start_date format. Use YYYY-MM-DD"}, 400
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return {"message": "Invalid end_date format. Use YYYY-MM-DD"}, 400

    # Validate date range
    if start_date > end_date:
        return {"message": "start_date cannot be after end_date"}, 400
    if end_date > datetime.now():
        return {"message": "end_date cannot be in the future"}, 400

    min_amount = None
    if min_amount_str:
        try:
            min_amount = float(min_amount_str)
            if min_amount < 0:
                return {"message": "min_amount cannot be negative"}, 400
        except ValueError:
            return {"message": "Invalid min_amount format. Must be a number"}, 400

    max_amount = None
    if max_amount_str:
        try:
            max_amount = float(max_amount_str)
            if max_amount < 0:
                return {"message": "max_amount cannot be negative"}, 400
        except ValueError:
            return {"message": "Invalid max_amount format. Must be a number"}, 400
    
    if min_amount is not None and max_amount is not None and min_amount > max_amount:
        return {"message": "min_amount cannot be greater than max_amount"}, 400

    filtered_transactions = []
    for transaction in dummy_transactions:
        transaction_dt = datetime.strptime(transaction["transaction_date"], '%Y-%m-%d')

        # Filter by date range
        if not (start_date <= transaction_dt <= end_date):
            continue

        # Filter by type
        if transaction_type and transaction_type.lower() != transaction["transaction_type"].lower():
            continue

        # Filter by amount
        if min_amount is not None and transaction["amount"] < min_amount:
            continue
        if max_amount is not None and transaction["amount"] > max_amount:
            continue

        filtered_transactions.append(transaction)
    
    if not filtered_transactions:
        return {"message": "No transactions found for the selected criteria."}, 404

    return filtered_transactions, 200

@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions, status_code = get_filtered_transactions()
    return jsonify(transactions), status_code

@app.route('/transactions/download-pdf', methods=['GET'])
def download_pdf():
    filtered_transactions, status_code = get_filtered_transactions()

    if status_code != 200:
        return jsonify(filtered_transactions), status_code
    
    if not filtered_transactions or (isinstance(filtered_transactions, dict) and filtered_transactions.get("message")):
        return jsonify({"message": "No transactions found for the selected criteria to generate PDF."}), 404

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 50, "Transaction Statement")
    c.drawString(100, height - 70, f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    y_position = height - 100
    for transaction in filtered_transactions:
        if y_position < 100: # New page if content goes too low
            c.showPage()
            y_position = height - 50
            c.drawString(100, y_position, "Transaction Statement (continued)")
            y_position -= 30

        c.drawString(100, y_position, f"Date: {transaction['transaction_date']}")
        c.drawString(200, y_position, f"Type: {transaction['transaction_type'].capitalize()}")
        c.drawString(300, y_position, f"Amount: {transaction['currency']} {transaction['amount']:.2f}")
        c.drawString(450, y_position, f"Description: {transaction['description']}")
        y_position -= 20

    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='transaction_statement.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
