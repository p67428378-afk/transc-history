import os

class Config:
    # Secret key for Flask application (replace with a strong, random key in production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_changed'

    # Database configuration (example for a PostgreSQL database)
    # In a real application, this would connect to the actual banking transaction database.
    # For this demo, we'll simulate a database.
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///transactions.db'

    # Other configurations can be added here
