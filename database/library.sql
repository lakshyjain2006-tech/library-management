-- ============================================================
--  Library Management System – SQL Schema & Seed Data
--  Compatible with: SQLite (default) and MySQL/PostgreSQL
--  Note: The app uses SQLAlchemy which auto-creates these
--        tables via db.create_all(). This file is provided
--        for reference, manual setup, or migration purposes.
-- ============================================================


-- ------------------------------------------------------------
-- 1. USERS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER      PRIMARY KEY AUTOINCREMENT,
    username      VARCHAR(80)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'member',  -- 'admin' | 'member'
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 2. BOOKS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    id               INTEGER      PRIMARY KEY AUTOINCREMENT,
    title            VARCHAR(200) NOT NULL,
    author           VARCHAR(150) NOT NULL,
    isbn             VARCHAR(20)  NOT NULL UNIQUE,
    category         VARCHAR(80),
    total_copies     INTEGER      NOT NULL DEFAULT 1,
    available_copies INTEGER      NOT NULL DEFAULT 1,
    added_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 3. ISSUES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS issues (
    id          INTEGER     PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER     NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    book_id     INTEGER     NOT NULL REFERENCES books(id)  ON DELETE CASCADE,
    issue_date  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date    DATETIME    NOT NULL,
    return_date DATETIME,
    status      VARCHAR(20) NOT NULL DEFAULT 'issued',     -- 'issued' | 'returned'
    fine        REAL        NOT NULL DEFAULT 0.0
);

-- Index for fast lookups by user and status
CREATE INDEX IF NOT EXISTS idx_issues_user   ON issues(user_id);
CREATE INDEX IF NOT EXISTS idx_issues_book   ON issues(book_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);


-- ============================================================
--  SEED DATA  (sample records for development / testing)
-- ============================================================

-- Admin user  (password: Admin@123)
-- Hash generated with werkzeug.security.generate_password_hash('Admin@123')
INSERT OR IGNORE INTO users (username, email, password_hash, role) VALUES
(
    'admin',
    'admin@library.com',
    'scrypt:32768:8:1$placeholder$hashed_value_replace_me',
    'admin'
);

-- Member users  (password: Member@123)
INSERT OR IGNORE INTO users (username, email, password_hash, role) VALUES
(
    'alice',
    'alice@example.com',
    'scrypt:32768:8:1$placeholder$hashed_value_replace_me',
    'member'
),
(
    'bob',
    'bob@example.com',
    'scrypt:32768:8:1$placeholder$hashed_value_replace_me',
    'member'
);

-- Sample books
INSERT OR IGNORE INTO books (title, author, isbn, category, total_copies, available_copies) VALUES
('The Great Gatsby',                  'F. Scott Fitzgerald', '978-0743273565', 'Fiction',         3, 3),
('To Kill a Mockingbird',             'Harper Lee',          '978-0061935466', 'Fiction',         2, 2),
('1984',                              'George Orwell',       '978-0451524935', 'Dystopian',       4, 4),
('Clean Code',                        'Robert C. Martin',    '978-0132350884', 'Technology',      2, 2),
('The Pragmatic Programmer',          'David Thomas',        '978-0135957059', 'Technology',      2, 2),
('Introduction to Algorithms',        'Cormen et al.',       '978-0262033848', 'Computer Science',3, 3),
('Sapiens: A Brief History',          'Yuval Noah Harari',   '978-0062316097', 'History',         2, 2),
('Atomic Habits',                     'James Clear',         '978-0735211292', 'Self-Help',       3, 3),
('The Alchemist',                     'Paulo Coelho',        '978-0062315007', 'Fiction',         2, 2),
('Python Crash Course',               'Eric Matthes',        '978-1593279288', 'Technology',      3, 3);
