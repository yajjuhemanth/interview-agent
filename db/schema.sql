CREATE DATABASE IF NOT EXISTS interview_db;
USE interview_db;

CREATE TABLE IF NOT EXISTS interview_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT NOT NULL,
    questions TEXT NOT NULL,
    qa TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
