-- =========================================================
-- USER QUERIES
-- =========================================================


-- Get all users

SELECT
    user_id,
    name,
    email,
    created_at
FROM users;


-- Get user by ID

SELECT
    user_id,
    name,
    email,
    created_at
FROM users
WHERE user_id = %s;


-- Get user by email

SELECT
    user_id,
    name,
    email,
    password,
    created_at
FROM users
WHERE email = %s;


-- Create user

INSERT INTO users
(
    name,
    email,
    password
)
VALUES
(
    %s,
    %s,
    %s
);


-- Update user

UPDATE users

SET
    name = %s,
    email = %s

WHERE user_id = %s;


-- Delete user

DELETE FROM users

WHERE user_id = %s;