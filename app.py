from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_file
from io import BytesIO
from transactions import get_transactions_data
from pdf_generator import generate_transaction_pdf

app = Flask(__name__)

def parse_date_param(date_str, param_name):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format for {param_name}. Expected YYYY-MM-DD.")
    return None

def parse_float_param(float_str, param_name):
    if float_str:
        try:
            return float(float_str)
        except ValueError:
            raise ValueError(f"Invalid number format for {param_name}. Expected a numeric value.")
    return None

@app.route('/transactions', methods=['GET'])
def get_transactions():
    """
    Retrieves a list of transactions based on provided filters.

    Query Parameters:
        start_date (str, optional): Start date for filtering (YYYY-MM-DD).
        end_date (str, optional): End date for filtering (YYYY-MM-DD).
        transaction_type (str, optional): Filter by 'credit' or 'debit'.
        min_amount (float, optional): Minimum transaction amount.
        max_amount (float, optional): Maximum transaction amount.

    Returns:
        json: A list of filtered transactions or an error message.
    """
    try:
        start_date = parse_date_param(request.args.get('start_date'), 'start_date')
        end_date = parse_date_param(request.args.get('end_date'), 'end_date')
        transaction_type = request.args.get('transaction_type')
        min_amount = parse_float_param(request.args.get('min_amount'), 'min_amount')
        max_amount = parse_float_param(request.args.get('max_amount'), 'max_amount')

        if start_date and end_date and start_date > end_date:
            return jsonify({"error": "Invalid date range: start_date cannot be after end_date"}), 400
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            return jsonify({"error": "Invalid amount range: min_amount cannot be greater than max_amount"}), 400
        if min_amount is not None and min_amount < 0:
            return jsonify({"error": "Invalid amount: min_amount cannot be negative"}), 400
        if max_amount is not None and max_amount < 0:
            return jsonify({"error": "Invalid amount: max_amount cannot be negative"}), 400

        transactions = get_transactions_data(
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            min_amount=min_amount,
            max_amount=max_amount
        )

        if not transactions:
            return jsonify({"message": "No transactions found for the selected criteria."}), 404

        # Format dates for JSON response
        formatted_transactions = []
        for transaction in transactions:
            transaction_copy = transaction.copy()
            transaction_copy['transaction_date'] = transaction_copy['transaction_date'].strftime('%Y-%m-%d')
            formatted_transactions.append(transaction_copy)

        return jsonify(formatted_transactions), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/transactions/download_pdf', methods=['GET'])
def download_transactions_pdf():
    """
    Generates and downloads a PDF statement of the filtered transaction history.

    Query Parameters:
        start_date (str, optional): Start date for filtering (YYYY-MM-DD).
        end_date (str, optional): End date for filtering (YYYY-MM-DD).
        transaction_type (str, optional): Filter by 'credit' or 'debit'.
        min_amount (float, optional): Minimum transaction amount.
        max_amount (float, optional): Maximum transaction amount.

    Returns:
        file: A PDF file containing the filtered transactions or an error message.
    """
    try:
        start_date = parse_date_param(request.args.get('start_date'), 'start_date')
        end_date = parse_date_param(request.args.get('end_date'), 'end_date')
        transaction_type = request.args.get('transaction_type')
        min_amount = parse_float_param(request.args.get('min_amount'), 'min_amount')
        max_amount = parse_float_param(request.args.get('max_amount'), 'max_amount')

        if start_date and end_date and start_date > end_date:
            return jsonify({"error": "Invalid date range: start_date cannot be after end_date"}), 400
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            return jsonify({"error": "Invalid amount range: min_amount cannot be greater than max_amount"}), 400
        if min_amount is not None and min_amount < 0:
            return jsonify({"error": "Invalid amount: min_amount cannot be negative"}), 400
        if max_amount is not None and max_amount < 0:
            return jsonify({"error": "Invalid amount: max_amount cannot be negative"}), 400

        transactions = get_transactions_data(
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            min_amount=min_amount,
            max_amount=max_amount
        )

        buffer = BytesIO()
        generate_transaction_pdf(transactions, buffer)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='transaction_statement.pdf'
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during PDF generation: {e}")
        return jsonify({"error": "An internal server error occurred during PDF generation"}), 500

if __name__ == '__main__':
    app.run(debug=True)
