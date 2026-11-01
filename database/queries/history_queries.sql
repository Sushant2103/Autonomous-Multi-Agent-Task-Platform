-- =========================================================
-- EXECUTION HISTORY QUERIES
-- =========================================================


-- Create agent log

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
);


-- Get agent logs for a task

SELECT
    log_id,
    task_id,
    agent_name,
    action,
    result,
    created_at
FROM agent_logs
WHERE task_id = %s
ORDER BY created_at;


-- Save final task result

INSERT INTO task_results
(
    task_id,
    final_response
)
VALUES
(
    %s,
    %s
);


-- Get final task result

SELECT
    result_id,
    task_id,
    final_response,
    created_at
FROM task_results
WHERE task_id = %s
ORDER BY created_at DESC;


-- Get complete task history

SELECT
    t.task_id,
    t.user_request,
    t.status,
    t.created_at
FROM tasks t
WHERE t.task_id = %s;


-- Get all task history for a user

SELECT
    t.task_id,
    t.user_request,
    t.status,
    t.created_at
FROM tasks t
WHERE t.user_id = %s
ORDER BY t.created_at DESC;