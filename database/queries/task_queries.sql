-- =========================================================
-- TASK QUERIES
-- =========================================================


-- Create task

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
);


-- Get task by ID

SELECT
    task_id,
    user_id,
    user_request,
    status,
    created_at
FROM tasks
WHERE task_id = %s;


-- Get all tasks of a user

SELECT
    task_id,
    user_request,
    status,
    created_at
FROM tasks
WHERE user_id = %s
ORDER BY created_at DESC;


-- Update task status

UPDATE tasks

SET
    status = %s

WHERE task_id = %s;


-- Delete task

DELETE FROM tasks

WHERE task_id = %s;


-- Create task step

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
);


-- Update task step

UPDATE task_steps

SET
    status = %s,
    result = %s

WHERE
    task_id = %s
    AND step_number = %s;


-- Get task steps

SELECT
    step_id,
    task_id,
    step_number,
    description,
    assigned_agent,
    status,
    result
FROM task_steps
WHERE task_id = %s
ORDER BY step_number;