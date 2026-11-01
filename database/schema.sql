-- =========================================================
-- DATABASE
-- =========================================================

CREATE DATABASE IF NOT EXISTS autonomous_multi_agent;

USE autonomous_multi_agent;


-- =========================================================
-- USERS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS users (

    user_id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- TASKS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS tasks (

    task_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT,

    user_request TEXT NOT NULL,

    status VARCHAR(50) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);


-- =========================================================
-- TASK STEPS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS task_steps (

    step_id INT AUTO_INCREMENT PRIMARY KEY,

    task_id INT NOT NULL,

    step_number INT NOT NULL,

    description TEXT NOT NULL,

    assigned_agent VARCHAR(100),

    status VARCHAR(50) DEFAULT 'pending',

    result TEXT,

    FOREIGN KEY (task_id)
        REFERENCES tasks(task_id)
);


-- =========================================================
-- AGENT LOGS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS agent_logs (

    log_id INT AUTO_INCREMENT PRIMARY KEY,

    task_id INT,

    agent_name VARCHAR(100),

    action TEXT,

    result TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (task_id)
        REFERENCES tasks(task_id)
);


-- =========================================================
-- TASK RESULTS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS task_results (

    result_id INT AUTO_INCREMENT PRIMARY KEY,

    task_id INT,

    final_response TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (task_id)
        REFERENCES tasks(task_id)
);