from database.connection import get_connection


def execute_query(query, parameters=None):

    connection = get_connection()

    if connection is None:

        return {
            "status": "failed",
            "error": "Could not connect to MySQL."
        }

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            query,
            parameters or ()
        )

        if query.strip().upper().startswith("SELECT"):

            results = cursor.fetchall()

            return {
                "status": "success",
                "rows": results
            }

        connection.commit()

        return {
            "status": "success",
            "affected_rows": cursor.rowcount
        }

    except Exception as e:

        connection.rollback()

        return {
            "status": "failed",
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        connection.close()