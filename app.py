from flask import Flask, jsonify, request, send_file
from flask_restful import Resource, Api
from datetime import datetime
import io
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
api = Api(app)

# In-memory mock database for demonstration purposes
mock_transactions = [
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
    },
    {
        "transaction_id": "T002",
        "customer_id": "123",
        "account_number": "ACC001",
        "transaction_date": "2023-01-16",
        "transaction_type": "debit",
        "amount": 25.50,
        "currency": "USD",
        "description": "Grocery Shopping",
        "merchant_info": "SuperMart",
    },
    {
        "transaction_id": "T003",
        "customer_id": "123",
        "account_number": "ACC001",
        "transaction_date": "2023-02-01",
        "transaction_type": "credit",
        "amount": 500.00,
        "currency": "USD",
        "description": "Bonus",
        "merchant_info": "Employer Inc.",
    },
    {
        "transaction_id": "T004",
        "customer_id": "123",
        "account_number": "ACC001",
        "transaction_date": "2023-03-10",
        "transaction_type": "debit",
        "amount": 120.00,
        "currency": "USD",
        "description": "Utility Bill",
        "merchant_info": "PowerCo",
    },
    {
        "transaction_id": "T005",
        "customer_id": "123",
        "account_number": "ACC001",
        "transaction_date": "2024-01-05",
        "transaction_type": "credit",
        "amount": 75.00,
        "currency": "USD",
        "description": "Refund",
        "merchant_info": "Retailer X",
    },
    {
        "transaction_id": "T006",
        "customer_id": "123",
        "account_number": "ACC001",
        "transaction_date": "2024-02-20",
        "transaction_type": "debit",
        "amount": 300.00,
        "currency": "USD",
        "description": "Rent",
        "merchant_info": "Landlord LLC",
    },
    {
        "transaction_id": "T007",
        "customer_id": "456",
        "account_number": "ACC002",
        "transaction_date": "2024-01-25",
        "transaction_type": "credit",
        "amount": 2000.00,
        "currency": "USD",
        "description": "Salary",
        "merchant_info": "Another Employer",
    },
]

def generate_pdf_statement(transactions):
    """Simulates PDF generation and returns a BytesIO object."""
    # In a real application, this would use a library like ReportLab or FPDF
    # to create a properly formatted PDF. For this mock, we'll just return
    # a simple text-based PDF simulation.
    output = io.BytesIO()
    output.write(b"Bank Statement\n\n")
    output.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n".encode())
    if not transactions:
        output.write(b"No transactions found for the selected criteria.\n")
    else:
        for t in transactions:
            output.write(
                f"Date: {t['transaction_date']}, Type: {t['transaction_type'].capitalize()}, "
                f"Amount: {t['currency']} {t['amount']:.2f}, Desc: {t['description']}\n".encode()
            )
    output.seek(0)
    return output


class TransactionHistory(Resource):
    def get(self):
        customer_id = request.args.get("customer_id")
        if not customer_id:
            return {"message": "customer_id is required"}, 400

        # Default to last 12 months
        end_date_str = request.args.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            return {"message": "Invalid end_date format. Use YYYY-MM-DD"}, 400

        start_date_str = request.args.get("start_date")
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                return {"message": "Invalid start_date format. Use YYYY-MM-DD"}, 400
        else:
            start_date = end_date - relativedelta(months=12)

        if start_date > end_date:
            return {"message": "start_date cannot be after end_date"}, 400
        if end_date > datetime.now():
            return {"message": "end_date cannot be in the future"}, 400

        transaction_type = request.args.get("type")
        min_amount = request.args.get("min_amount", type=float)
        max_amount = request.args.get("max_amount", type=float)

        if min_amount is not None and min_amount < 0:
            return {"message": "min_amount cannot be negative"}, 400
        if max_amount is not None and max_amount < 0:
            return {"message": "max_amount cannot be negative"}, 400
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            return {"message": "min_amount cannot be greater than max_amount"}, 400

        filtered_transactions = []
        for t in mock_transactions:
            if t["customer_id"] != customer_id:
                continue

            t_date = datetime.strptime(t["transaction_date"], "%Y-%m-%d")

            if not (start_date <= t_date <= end_date):
                continue

            if transaction_type and t["transaction_type"] != transaction_type.lower():
                continue

            if min_amount is not None and t["amount"] < min_amount:
                continue

            if max_amount is not None and t["amount"] > max_amount:
                continue

            filtered_transactions.append(t)

        if not filtered_transactions:
            return {"message": "No transactions found for the selected criteria."}, 200

        return jsonify(filtered_transactions)


class TransactionDownload(Resource):
    def get(self):
        customer_id = request.args.get("customer_id")
        if not customer_id:
            return {"message": "customer_id is required"}, 400

        # Re-use filtering logic from TransactionHistory
        # This is a simplified approach; in a real app, you might refactor
        # the filtering logic into a separate service/module.
        with app.test_request_context(path='/transactions', query_string=request.args):
            response = TransactionHistory().get()
            if response[1] != 200: # Check status code
                return response # Return error from TransactionHistory
            
            filtered_transactions = response[0].json # Extract JSON data from response

        if not filtered_transactions:
            return {"message": "No transactions found for the selected criteria."}, 200

        pdf_output = generate_pdf_statement(filtered_transactions)
        return send_file(
            pdf_output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"transactions_{customer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
        )


api.add_resource(TransactionHistory, "/transactions")
api.add_resource(TransactionDownload, "/transactions/download")

if __name__ == "__main__":
    app.run(debug=True)
