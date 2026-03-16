# Transaction History Management System

This project implements a backend service for managing customer transaction history, allowing users to view, filter, and download their transaction statements as PDFs. This service is part of a larger banking management system, adhering to a microservices architecture.

## Features

*   **View Transaction History**: Display a detailed, chronological list of transactions.
*   **Filter by Date Range**: Filter transactions by specifying a start and end date (defaults to the last 12 months).
*   **Filter by Transaction Type**: Filter by 'Credit' or 'Debit' transaction types.
*   **Filter by Amount**: Filter transactions by a specific amount or a range.
*   **Download PDF Statement**: Generate and download a PDF document of the currently filtered transaction history.

## Architecture

The system follows a microservices architecture, with two primary services:

1.  **Transaction History Service**: A Flask application responsible for retrieving, filtering, and serving transaction data from an existing banking transaction database.
2.  **PDF Generation Service**: A utility (simulated in this implementation) that generates PDF documents from transaction data.

Communication between services and with the frontend is RESTful over HTTPS.

## Technologies Used

*   **Backend**: Python 3.9+
*   **Web Framework**: Flask
*   **PDF Generation**: ReportLab (simulated for this implementation)
*   **Containerization**: Docker
*   **Orchestration**: Kubernetes (GKE - for deployment, not part of this codebase)
*   **Database**: Existing Banking Transaction Database (SQL-based, simulated interaction)

## Setup and Local Development

### Prerequisites

*   Python 3.9+
*   `pip` (Python package installer)
*   `git`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/p67428378-afk/transc-history.git
    cd transc-history
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

The application can be run using Flask's development server:

```bash
flask run
```

The API will be available at `http://127.0.0.1:5000`.

### API Endpoints

*   **GET /transactions**: Retrieve transaction history.
    *   **Query Parameters**:
        *   `customer_id` (required): ID of the customer.
        *   `start_date` (optional): Start date for filtering (YYYY-MM-DD). Defaults to 12 months ago.
        *   `end_date` (optional): End date for filtering (YYYY-MM-DD). Defaults to today.
        *   `type` (optional): Transaction type ('credit' or 'debit').
        *   `min_amount` (optional): Minimum transaction amount.
        *   `max_amount` (optional): Maximum transaction amount.
    *   **Example**: `/transactions?customer_id=123&start_date=2023-01-01&end_date=2023-06-30&type=credit`

*   **GET /transactions/download**: Download transaction history as PDF.
    *   **Query Parameters**: Same as `/transactions`.
    *   **Example**: `/transactions/download?customer_id=123&type=debit`

## Docker

To build and run the application using Docker:

1.  **Build the Docker image:**
    ```bash
    docker build -t transaction-history-service .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 5000:5000 transaction-history-service
    ```

The application will be accessible at `http://localhost:5000`.

## Testing

Unit and integration tests are located in the `tests/` directory.

To run tests:

```bash
pytest
```

## Contributing

Please refer to the project's contribution guidelines (if any) for details on how to contribute.

## License

This project is licensed under the [MIT License](LICENSE).
