-- VAANI Database Schema
-- PostgreSQL Database for ISL Recognition Platform

-- ============================================
-- USER MANAGEMENT TABLES
-- ============================================

-- Regular users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin users table
CREATE TABLE IF NOT EXISTS admins (
    admin_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- NGO MANAGEMENT TABLES
-- ============================================

-- NGO partnership requests
CREATE TABLE IF NOT EXISTS ngo_requests (
    request_id SERIAL PRIMARY KEY,
    org_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
    purpose TEXT NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by INTEGER REFERENCES admins(admin_id)
);

-- NGO accounts (created after approval)
CREATE TABLE IF NOT EXISTS ngo_accounts (
    ngo_id SERIAL PRIMARY KEY,
    request_id INTEGER UNIQUE REFERENCES ngo_requests(request_id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Add is_active column if it doesn't exist (for existing databases)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='ngo_accounts' AND column_name='is_active'
    ) THEN
        ALTER TABLE ngo_accounts ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='ngo_accounts' AND column_name='last_login'
    ) THEN
        ALTER TABLE ngo_accounts ADD COLUMN last_login TIMESTAMP;
    END IF;
END $$;

-- ============================================
-- SIGN LANGUAGE DICTIONARY
-- ============================================

CREATE TABLE IF NOT EXISTS sign_dictionary (
    sign_id SERIAL PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    starting_letter VARCHAR(1) NOT NULL,
    video_path VARCHAR(500) NOT NULL,
    category VARCHAR(50),
    difficulty_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(word)
);

CREATE INDEX idx_sign_word ON sign_dictionary(word);
CREATE INDEX idx_sign_letter ON sign_dictionary(starting_letter);

-- ============================================
-- EVENTS MANAGEMENT
-- ============================================

CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    ngo_id INTEGER REFERENCES ngo_accounts(ngo_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    event_time TIME,
    location VARCHAR(255),
    city VARCHAR(100),
    registration_link VARCHAR(500),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'UPCOMING' CHECK (status IN ('UPCOMING', 'ONGOING', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_ngo ON events(ngo_id);

-- ============================================
-- USER ACTIVITY / HISTORY
-- ============================================

CREATE TABLE IF NOT EXISTS user_predictions (
    prediction_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    prediction_type VARCHAR(20) CHECK (prediction_type IN ('WORD', 'ALPHABET')),
    predicted_value VARCHAR(100),
    confidence DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_user ON user_predictions(user_id);
CREATE INDEX idx_predictions_date ON user_predictions(created_at);

-- ============================================
-- EMERGENCY CONTACTS (Optional Feature)
-- ============================================

CREATE TABLE IF NOT EXISTS emergency_contacts (
    contact_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    relationship VARCHAR(50),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DONATIONS / SUPPORT (Optional Feature)
-- ============================================

CREATE TABLE IF NOT EXISTS donations (
    donation_id SERIAL PRIMARY KEY,
    ngo_id INTEGER REFERENCES ngo_accounts(ngo_id) ON DELETE CASCADE,
    donor_name VARCHAR(255),
    donor_email VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255) UNIQUE,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED')),
    donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- VIEWS FOR EASIER QUERIES
-- ============================================

-- View: Approved NGOs with account info
CREATE OR REPLACE VIEW approved_ngos AS
SELECT 
    n.ngo_id,
    nr.org_name,
    nr.contact_person,
    nr.email,
    nr.phone,
    nr.city,
    nr.description,
    nr.purpose,
    n.is_active,
    n.created_at,
    n.last_login
FROM ngo_accounts n
INNER JOIN ngo_requests nr ON n.request_id = nr.request_id
WHERE nr.status = 'APPROVED' AND n.is_active = TRUE;

-- View: Event details with NGO info
CREATE OR REPLACE VIEW event_details AS
SELECT 
    e.event_id,
    e.title,
    e.description,
    e.event_date,
    e.event_time,
    e.location,
    e.city,
    e.registration_link,
    e.contact_email,
    e.contact_phone,
    e.status,
    nr.org_name AS ngo_name,
    nr.email AS ngo_email
FROM events e
INNER JOIN ngo_accounts n ON e.ngo_id = n.ngo_id
INNER JOIN ngo_requests nr ON n.request_id = nr.request_id;

-- ============================================
-- SAMPLE ADMIN USER (for testing)
-- ============================================
-- Password: admin123
INSERT INTO admins (email, password_hash, full_name) 
VALUES ('admin@vaani.com', 'scrypt:32768:8:1$GvB8Fq7YKP4zLQXm$d1c8d5b5f3e9a6c7f2e4b8d9c6a3f1e5d7b9a2c4f6e8d0c2a4f6e8d0c2a4f6e8d0c2a4f6e8d0c2a4f6e8d0c2a4', 'Admin User')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_ngo_requests_status ON ngo_requests(status);
CREATE INDEX IF NOT EXISTS idx_ngo_requests_email ON ngo_requests(email);
CREATE INDEX IF NOT EXISTS idx_ngo_accounts_email ON ngo_accounts(email);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
