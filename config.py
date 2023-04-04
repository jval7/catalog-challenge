# import os


def get_db_connection_string():
    """
    Get the connection string for the database
    """
    # todo we can define the real connection string with a postgres db
    # host = os.environ.get("DB_HOST", "localhost")
    # port = 54321 if host == "localhost" else 5432
    # password = os.environ.get("DB_PASSWORD", "abc123")
    # user, db_name = "allocation", "allocation"
    return "sqlite:///product.db"
