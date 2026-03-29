# Transaction History Service

This service provides a RESTful API for customers to view, filter, and download their transaction history.

## Features

- View a detailed list of transactions.
- Filter transactions by date range, type (credit/debit), and amount.
- Download filtered transaction history as a PDF statement.

## Architecture

The service is built using Python Flask and follows a microservices architecture pattern. It interacts with a simulated transaction database and a PDF generation module.

## Setup Instructions

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/p67428378-afk/transc-history.git
    cd transc-history
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application:**
    ```bash
    export FLASK_APP=app.py
    flask run
    ```
    The API will be available at `http://127.0.0.1:5000`.

### Docker Deployment

1.  **Build the Docker image:**
    ```bash
    docker build -t transaction-history-service .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 5000:5000 transaction-history-service
    ```
    The API will be available at `http://localhost:5000`.

## API Endpoints

### 1. Get Transaction History

`GET /transactions`

**Description:** Retrieves a list of transactions, with optional filtering.

**Query Parameters:**

-   `start_date` (string, optional): Start date for filtering (YYYY-MM-DD). Defaults to 12 months ago.
-   `end_date` (string, optional): End date for filtering (YYYY-MM-DD). Defaults to today.
-   `transaction_type` (string, optional): Filter by 'credit' or 'debit'.
-   `min_amount` (float, optional): Minimum transaction amount.
-   `max_amount` (float, optional): Maximum transaction amount.

**Example Request:**
```
GET /transactions?start_date=2023-01-01&end_date=2023-03-31&transaction_type=debit&min_amount=50.00
```

**Example Response (200 OK):**
```json
[
    {
        "transaction_id": "...",
        "account_number": "...",
        "transaction_date": "YYYY-MM-DD",
        "transaction_type": "credit/debit",
        "amount": 100.00,
        "currency": "USD",
        "description": "..."
    },
    ...
]
```

**Error Responses:**
-   `400 Bad Request`: Invalid date format, invalid amount range, etc.
-   `404 Not Found`: No transactions found for the given criteria.

### 2. Download Transaction History as PDF

`GET /transactions/download_pdf`

**Description:** Generates and downloads a PDF statement of the filtered transaction history. Accepts the same query parameters as `/transactions`.

**Query Parameters:** Same as `/transactions`.

**Example Request:**
```
GET /transactions/download_pdf?start_date=2023-01-01&end_date=2023-03-31
```

**Example Response (200 OK):**
A PDF file will be downloaded.

**Error Responses:**
-   `400 Bad Request`: Invalid date format, invalid amount range, etc.
-   `404 Not Found`: No transactions found for the given criteria (PDF will indicate this).
-   `500 Internal Server Error`: Error during PDF generation.

## Running Tests

To run the unit and integration tests:

```bash
pytest
```
