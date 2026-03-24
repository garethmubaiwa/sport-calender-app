import mysql.connector
from mysql.connector import Error
from mysql.connector.abstracts import MySQLConnectionAbstract

def get_db_connection(config: dict) -> MySQLConnectionAbstract:
    """
    Establishes a connection to the MySQL database using the provided configuration.

    Args:
        config (dict): A dictionary containing the database connection parameters:
            - host (str): The hostname of the database server.
            - user (str): The username to connect to the database.
            - password (str): The password for the database user.
            - database (str): The name of the database to connect to.

    Returns:
        MySQLConnectionAbstract: A MySQLConnectionAbstract object if the connection is successful.

    Raises:
        Error: If there is an error connecting to the database, an exception will be raised with details about the error.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection # type: ignore
        else:
            raise Error("Connection was created but is not active.")
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        raise


def close_db_connection(connection: MySQLConnectionAbstract) -> None:
    """
    Closes the given database connection.

    Args:
        connection (MySQLConnectionAbstract): The database connection to be closed.

    Returns:
        None

    Raises:
        Error: If there is an error while closing the connection, an exception will be raised with details about the error.
    """
    try:
        if connection.is_connected():
            connection.close()
            print("Database connection closed successfully.")
        else:
            print("Connection is already closed.")
    except Error as e:
        print(f"Error while closing the database connection: {e}")
        raise