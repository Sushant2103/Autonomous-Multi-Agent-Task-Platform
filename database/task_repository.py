from database.connection import get_connection


# ============================================================
# CREATE TASK
# ============================================================

def create_task(user_id, user_request):

    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO tasks
        (
            user_id,
            user_request,
            status
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        """

        cursor.execute(
            query,
            (
                user_id,
                user_request,
                "running"
            )
        )

        connection.commit()

        task_id = cursor.lastrowid

        return task_id

    except Exception as e:

        connection.rollback()

        print(
            "Error creating task:",
            e
        )

        return None

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# CREATE TASK STEP
# ============================================================

def create_task_step(
    task_id,
    step_number,
    description,
    assigned_agent
):

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO task_steps
        (
            task_id,
            step_number,
            description,
            assigned_agent,
            status
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        cursor.execute(
            query,
            (
                task_id,
                step_number,
                description,
                assigned_agent,
                "pending"
            )
        )

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print(
            "Error creating task step:",
            e
        )

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# UPDATE TASK STEP
# ============================================================

def update_task_step(
    task_id,
    step_number,
    status,
    result
):

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:

        cursor = connection.cursor()

        query = """
        UPDATE task_steps
        SET
            status = %s,
            result = %s
        WHERE
            task_id = %s
            AND step_number = %s
        """

        cursor.execute(
            query,
            (
                status,
                str(result),
                task_id,
                step_number
            )
        )

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print(
            "Error updating task step:",
            e
        )

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# CREATE AGENT LOG
# ============================================================

def create_agent_log(
    task_id,
    agent_name,
    action,
    result
):

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO agent_logs
        (
            task_id,
            agent_name,
            action,
            result
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        """

        cursor.execute(
            query,
            (
                task_id,
                agent_name,
                action,
                str(result)
            )
        )

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print(
            "Error creating agent log:",
            e
        )

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# SAVE FINAL TASK RESULT
# ============================================================

def save_task_result(
    task_id,
    final_response
):

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO task_results
        (
            task_id,
            final_response
        )
        VALUES
        (
            %s,
            %s
        )
        """

        cursor.execute(
            query,
            (
                task_id,
                final_response
            )
        )

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print(
            "Error saving final result:",
            e
        )

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# UPDATE TASK STATUS
# ============================================================

def update_task_status(
    task_id,
    status
):

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:

        cursor = connection.cursor()

        query = """
        UPDATE tasks
        SET
            status = %s
        WHERE
            task_id = %s
        """

        cursor.execute(
            query,
            (
                status,
                task_id
            )
        )

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print(
            "Error updating task status:",
            e
        )

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()