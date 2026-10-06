-- DDL: Healthcare EDI Members Schema
CREATE TABLE IF NOT EXISTS members (
    member_id VARCHAR(50) PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    gender CHAR(1),
    dob CHAR(8),
    plan_type VARCHAR(20),
    coverage_code VARCHAR(10),
    effective_date CHAR(8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DDL: Audit Discrepancies Table
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id VARCHAR(50),
    issue_type VARCHAR(50),
    details TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AUDIT QUERY 1: Active Eligibility Summary by Coverage Plan
SELECT 
    coverage_code,
    plan_type,
    COUNT(member_id) AS total_enrolled_members
FROM members
GROUP BY coverage_code, plan_type
ORDER BY total_enrolled_members DESC;

-- AUDIT QUERY 2: Retroactive and Discrepancy Reconciliation
SELECT 
    m.member_id,
    m.last_name,
    m.first_name,
    a.issue_type,
    a.details,
    a.logged_at
FROM members m
INNER JOIN audit_logs a ON m.member_id = a.member_id;

-- AUDIT QUERY 3: Potential Coverage Overlaps / Duplicate Checks
SELECT 
    member_id, 
    COUNT(*) AS records_found
FROM members
GROUP BY member_id
HAVING COUNT(*) > 1;
