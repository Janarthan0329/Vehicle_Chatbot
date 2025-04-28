import mysql.connector

def get_db_connection():
    """
    Establish a connection to the MySQL database.
    """
    return mysql.connector.connect(
        host="localhost",  
        user="root",      
        password="new_password",  
        database="vehicles_db"  
    )
