# Transaction History Management System

This repository contains the backend services for a banking transaction history management system. It allows customers to view, filter, and download their transaction statements.

## Services

*   **Transaction History Service**: A Python Flask application responsible for retrieving and filtering transaction data from the banking database.
*   **PDF Generation Service**: (To be implemented) A service responsible for generating PDF statements from filtered transaction data.

## Setup and Development

### Prerequisites

*   Docker
*   Docker Compose (optional, for local development)
*   Python 3.9+
*   Poetry (for dependency management, recommended) or pip

### Local Development (Transaction History Service)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/p67428378-afk/transc-history.git
    cd transc-history
    ```

2.  **Navigate to the Transaction History Service directory:**
    ```bash
    cd transaction_history_service
    ```

3.  **Set up environment variables:**
    Create a `.env` file based on `.env.example`:
    ```bash
    cp .env.example .env
    # Edit .env with your database connection details
    ```

4.  **Install dependencies:**
    Using Poetry (recommended):
    ```bash
    poetry install
    poetry shell
    ```
    Using pip:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the service:**
    ```bash
    flask run
    ```
    The service will be available at `http://127.0.0.1:5000`.

### API Endpoints (Transaction History Service)

*   `GET /transactions`: Retrieve and filter transaction history.
    *   **Query Parameters**:
        *   `customer_id` (required): The ID of the customer.
        *   `start_date` (optional): Start date for filtering (YYYY-MM-DD).
        *   `end_date` (optional): End date for filtering (YYYY-MM-DD).
        *   `transaction_type` (optional): 'credit' or 'debit'.
        *   `min_amount` (optional): Minimum transaction amount.
        *   `max_amount` (optional): Maximum transaction amount.
        *   `page` (optional): Page number for pagination (default: 1).
        *   `per_page` (optional): Number of items per page (default: 20).

### Database Setup

This service expects an existing PostgreSQL database. Ensure your `.env` file is configured correctly to connect to it.

## Deployment

The services are containerized using Docker and designed for deployment on Kubernetes (GKE). Refer to the `Dockerfile` in each service directory for containerization details. CI/CD pipelines will handle automated builds and deployments.
