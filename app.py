import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from faker import Faker
import random
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from models import db, Transaction
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
faker = Faker()

# Helper function to generate dummy transactions
def generate_dummy_transactions(num_transactions=100, account_number='1234567890'):
    with app.app_context():
        if Transaction.query.count() == 0:
            print("Generating dummy transactions...")
            for _ in range(num_transactions):
                transaction_date = faker.date_time_between(start_date='-2y', end_date='now')
                transaction_type = random.choice(['credit', 'debit'])
                amount = round(random.uniform(5.0, 1000.0), 2)
                description = faker.sentence(nb_words=6)
                merchant_info = faker.company()

                transaction = Transaction(
                    account_number=account_number,
                    transaction_date=transaction_date,
                    transaction_type=transaction_type,
                    amount=amount,
                    description=description,
                    merchant_info=merchant_info
                )
                db.session.add(transaction)
            db.session.commit()
            print(f"Generated {num_transactions} dummy transactions.")
        else:
            print("Dummy transactions already exist.")

@app.before_request
def create_tables():
    with app.app_context():
        db.create_all()
        generate_dummy_transactions()

@app.route('/transactions', methods=['GET'])
def get_transactions():
    account_number = request.args.get('account_number', '1234567890') # Default for dummy data
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    transaction_type = request.args.get('type')
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)

    query = Transaction.query.filter_by(account_number=account_number)

    # Default to last 12 months
    if not start_date_str and not end_date_str:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
    else:
        try:
            if start_date_str: 
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            else:
                start_date = datetime.min # No start date filter
            if end_date_str: 
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            else:
                end_date = datetime.max # No end date filter
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if start_date and end_date:
        if start_date > end_date:
            return jsonify({'error': 'Start date cannot be after end date.'}), 400
        query = query.filter(Transaction.transaction_date.between(start_date, end_date + timedelta(days=1)))
    elif start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    elif end_date:
        query = query.filter(Transaction.transaction_date <= end_date + timedelta(days=1))

    if transaction_type:
        if transaction_type.lower() not in ['credit', 'debit']:
            return jsonify({'error': 'Invalid transaction type. Use "credit" or "debit".'}), 400
        query = query.filter_by(transaction_type=transaction_type.lower())

    if min_amount is not None:
        if min_amount < 0:
            return jsonify({'error': 'Minimum amount cannot be negative.'}), 400
        query = query.filter(Transaction.amount >= min_amount)

    if max_amount is not None:
        if max_amount < 0:
            return jsonify({'error': 'Maximum amount cannot be negative.'}), 400
        query = query.filter(Transaction.amount <= max_amount)

    transactions = query.order_by(Transaction.transaction_date.desc()).all()

    if not transactions:
        return jsonify({'message': 'No transactions found for the selected criteria.'}), 404

    return jsonify([t.to_dict() for t in transactions])

@app.route('/transactions/download-pdf', methods=['GET'])
def download_transactions_pdf():
    account_number = request.args.get('account_number', '1234567890') # Default for dummy data
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    transaction_type = request.args.get('type')
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)

    # Re-use the filtering logic from get_transactions
    with app.test_request_context(query_string=request.query_string):
        response = get_transactions()
        if response.status_code != 200:
            # Handle errors from get_transactions, e.g., invalid date format
            return response
        
        transactions_data = response.get_json()

    if not transactions_data or transactions_data == {'message': 'No transactions found for the selected criteria.'}:
        # Create a PDF indicating no transactions
        buffer = create_no_transactions_pdf(account_number, start_date_str, end_date_str, transaction_type, min_amount, max_amount)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=transaction_statement_no_data.pdf'
        return response

    # Generate PDF
    buffer = create_transactions_pdf(transactions_data, account_number)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=transaction_statement.pdf'
    return response

def create_transactions_pdf(transactions_data, account_number):
    from io import BytesIO
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Transaction Statement", styles['h1']))
    story.append(Paragraph(f"Account Number: {account_number}", styles['h2']))
    story.append(Spacer(1, 0.2 * 2.54 * 72))

    data = [['Date', 'Type', 'Description', 'Merchant', 'Amount', 'Currency']]
    for t in transactions_data:
        data.append([
            datetime.fromisoformat(t['transaction_date']).strftime('%Y-%m-%d'),
            t['transaction_type'].capitalize(),
            t['description'],
            t['merchant_info'],
            f"{t['amount']:.2f}",
            t['currency']
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer

def create_no_transactions_pdf(account_number, start_date_str, end_date_str, transaction_type, min_amount, max_amount):
    from io import BytesIO
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Transaction Statement", styles['h1']))
    story.append(Paragraph(f"Account Number: {account_number}", styles['h2']))
    story.append(Spacer(1, 0.2 * 2.54 * 72))
    story.append(Paragraph("No transactions found for the selected criteria.", styles['Normal']))
    story.append(Spacer(1, 0.2 * 2.54 * 72))

    filter_details = []
    if start_date_str: filter_details.append(f"Start Date: {start_date_str}")
    if end_date_str: filter_details.append(f"End Date: {end_date_str}")
    if transaction_type: filter_details.append(f"Type: {transaction_type.capitalize()}")
    if min_amount is not None: filter_details.append(f"Min Amount: {min_amount:.2f}")
    if max_amount is not None: filter_details.append(f"Max Amount: {max_amount:.2f}")

    if filter_details:
        story.append(Paragraph("Applied Filters:", styles['h3']))
        for detail in filter_details:
            story.append(Paragraph(detail, styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        generate_dummy_transactions()
    app.run(debug=True)
