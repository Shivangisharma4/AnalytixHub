web: gunicorn api_server:app
migrate: python -c "from database import DatabaseManager; DatabaseManager().init_database()"
scrape: python main.py all
