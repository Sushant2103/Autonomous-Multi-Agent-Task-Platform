import os

import mysql.connector
from mysql.connector import Error

from dotenv import load_dotenv


load_dotenv()


def get_connection():

    try:

        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )

        if connection.is_connected():

            print("MySQL connection successful.")

            return connection

    except Error as e:

        print("MySQL connection failed.")
        print("Error:", e)

        return None