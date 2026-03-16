from flask import Flask, request, jsonify, send_file, Response
from datetime import datetime, timedelta
import io
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config.from_object('config.Config')

# Dynamic Dummy Data Generation
def generate_dummy_transactions(num_transactions=15):
    transactions = []
    today = datetime.now()
    for i in range(num_transactions):
        days_ago = i * 20 # Spread transactions over time
        transaction_date = today - timedelta(days=days_ago)
        transaction_type = "credit" if i % 3 == 0 else "debit"
        amount = round(10 + i * 10 + (i % 5) * 2.5, 2)
        description = f"Transaction {i+1}"
        merchant_info = f"Merchant {chr(65 + i)}"

        transactions.append({
            "transaction_id": f"T{i+1:03d}",
            "account_number": "ACC001",
            "transaction_date": transaction_date.strftime('%Y-%m-%d'),
            "transaction_type": transaction_type,
            "amount": amount,
            "currency": "USD",
            "description": description,
            "merchant_info": merchant_info,
        })
    return transactions

dummy_transactions = generate_dummy_transactions()

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
