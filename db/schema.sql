-- Users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20)
        CHECK (role IN ('applicant', 'employer', 'admin'))
        DEFAULT 'applicant',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employers
CREATE TABLE employers (
    employer_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    company_name VARCHAR(150) NOT NULL,
    description TEXT,
    website VARCHAR(200),
    location VARCHAR(100)
);

-- Jobs
CREATE TABLE jobs (
    job_id SERIAL PRIMARY KEY,
    employer_id INT REFERENCES employers(employer_id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    job_type VARCHAR(50)
        CHECK (job_type IN ('full-time', 'part-time', 'gig', 'temporary', 'internship')),
    location VARCHAR(100),
    pay_range VARCHAR(50),
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Applications
CREATE TABLE applications (
    application_id SERIAL PRIMARY KEY,
    job_id INT REFERENCES jobs(job_id) ON DELETE CASCADE,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    cover_letter TEXT,
    status VARCHAR(20)
        CHECK (status IN ('pending', 'reviewed', 'accepted', 'rejected'))
        DEFAULT 'pending',
    date_applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (job_id, user_id)
);

-- Notifications
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial Resources
CREATE TABLE financial_resources (
    resource_id SERIAL PRIMARY KEY,
    website VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL
        CHECK (resource_type IN ('credit', 'budget', 'invest')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Indexes
CREATE INDEX idx_jobs_location     ON jobs(location);
CREATE INDEX idx_jobs_type         ON jobs(job_type);
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);

