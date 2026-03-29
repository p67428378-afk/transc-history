import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from sqlalchemy import and_, cast, Date
from sqlalchemy.orm import joinedload
from dotenv import load_dotenv

from .database import SessionLocal, engine, init_db, get_db
from .models import Customer, Transaction, TransactionType, Base

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')

@app.route("/transactions", methods=["GET"])
def get_transactions():
    customer_id = request.args.get("customer_id")
    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400

    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        query = db.query(Transaction).filter(Transaction.account_number == customer.account_number)

        # Default to last 12 months
        end_date = request.args.get("end_date")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_date = datetime.now()

        start_date = request.args.get("start_date")
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_date = end_date - timedelta(days=365)

        if start_date > end_date:
            return jsonify({"error": "Start date cannot be after end date"}), 400
        if end_date > datetime.now():
            return jsonify({"error": "End date cannot be in the future"}), 400

        query = query.filter(and_(
            cast(Transaction.transaction_date, Date) >= start_date.date(),
            cast(Transaction.transaction_date, Date) <= end_date.date()
        ))

        transaction_type = request.args.get("transaction_type")
        if transaction_type:
            try:
                query = query.filter(Transaction.transaction_type == TransactionType[transaction_type.upper()])
            except KeyError:
                return jsonify({"error": "Invalid transaction_type. Must be 'credit' or 'debit'"}), 400

        min_amount = request.args.get("min_amount")
        if min_amount:
            try:
                min_amount = float(min_amount)
                if min_amount < 0:
                    return jsonify({"error": "min_amount cannot be negative"}), 400
                query = query.filter(Transaction.amount >= min_amount)
            except ValueError:
                return jsonify({"error": "Invalid min_amount"}), 400

        max_amount = request.args.get("max_amount")
        if max_amount:
            try:
                max_amount = float(max_amount)
                if max_amount < 0:
                    return jsonify({"error": "max_amount cannot be negative"}), 400
                query = query.filter(Transaction.amount <= max_amount)
            except ValueError:
                return jsonify({"error": "Invalid max_amount"}), 400

        if min_amount and max_amount and min_amount > max_amount:
            return jsonify({"error": "min_amount cannot be greater than max_amount"}), 400

        # Pagination
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        offset = (page - 1) * per_page

        total_transactions = query.count()
        transactions = query.order_by(Transaction.transaction_date.desc()).offset(offset).limit(per_page).all()

        if not transactions and total_transactions == 0:
            return jsonify({"message": "No transactions found for this customer.", "transactions": []}), 200
        elif not transactions:
            return jsonify({"message": "No transactions found for the selected criteria.", "transactions": []}), 200

        results = []
        for transaction in transactions:
            results.append({
                "transaction_id": transaction.transaction_id,
                "account_number": transaction.account_number,
                "transaction_date": transaction.transaction_date.isoformat(),
                "transaction_type": transaction.transaction_type.value,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "description": transaction.description,
                "merchant_info": transaction.merchant_info
            })

        return jsonify({
            "transactions": results,
            "total_transactions": total_transactions,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_transactions + per_page - 1) // per_page
        })

    except Exception as e:
        app.logger.error(f"Error retrieving transactions: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500
    finally:
        db.close()

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
