# NGO Tables Structure Fix

## Problem
The original code had an inconsistency:
- NGO data was stored in `ngo_requests` table only
- Login was attempting to query `ngo_accounts` table
- This caused authentication failures and data inconsistencies

## Solution

### New Structure:
1. **`ngo_requests`** - Stores partnership applications (PENDING/APPROVED/REJECTED)
2. **`ngo_accounts`** - Created only after approval, stores login credentials
3. **Proper JOIN** - API endpoints join both tables to get complete info

### Key Changes:

#### 1. Database Schema ([database/schema.sql](schema.sql))
- Proper table structure with foreign keys
- `ngo_accounts.request_id` references `ngo_requests.request_id`
- Added `is_active` flag for account management
- Created view `approved_ngos` for easier queries

#### 2. API Endpoints ([backend/app.py](../backend/app.py))

**GET `/api/ngos`** - Fixed to join tables:
```sql
SELECT n.ngo_id, nr.org_name, nr.contact_person, ...
FROM ngo_accounts n
INNER JOIN ngo_requests nr ON n.request_id = nr.request_id
WHERE nr.status = 'APPROVED' AND n.is_active = TRUE
```

**POST `/api/admin/ngo-request/action`** - Approval creates account:
```sql
-- Updates ngo_requests.status
-- Creates entry in ngo_accounts with password
-- Sends email notification
```

**POST `/api/ngo/login`** - Authenticates from ngo_accounts:
```sql
SELECT ngo_id, password_hash 
FROM ngo_accounts 
WHERE email = ?
```

## Setup Instructions

### Option 1: Fresh Setup
```bash
# Set DATABASE_URL in .env file
DATABASE_URL=postgresql://user:password@localhost:5432/vaani_db

# Run setup script
python database/setup_db.py
```

### Option 2: Manual Migration
```bash
# Connect to PostgreSQL
psql -U postgres -d vaani_db

# Run schema file
\i database/schema.sql
```

## Data Flow

```
1. NGO submits partnership request
   → Creates row in ngo_requests (status=PENDING)

2. Admin reviews request
   → Updates ngo_requests.status to APPROVED/REJECTED

3. If APPROVED:
   → Creates entry in ngo_accounts
   → Generates temporary password
   → Sends email with credentials

4. NGO logs in:
   → Queries ngo_accounts for authentication
   → Joins with ngo_requests for org info

5. NGO dashboard:
   → Can post events
   → Manage profile
   → View analytics
```

## Verification

After running the setup, verify tables exist:
```sql
-- Check tables
\dt

-- Check NGO accounts with organization info
SELECT * FROM approved_ngos;

-- Check login works
SELECT email, created_at 
FROM ngo_accounts 
WHERE is_active = TRUE;
```

## Benefits

✅ **Data Integrity** - Foreign key constraints ensure consistency  
✅ **Security** - Passwords stored separately from application data  
✅ **Flexibility** - Can disable accounts without deleting requests  
✅ **Audit Trail** - Complete history of requests and approvals  
✅ **Performance** - Indexed queries for faster lookups  

## Troubleshooting

### Error: relation "ngo_accounts" does not exist
Run: `python database/setup_db.py`

### Error: duplicate key value violates unique constraint
The email already has an account. Check:
```sql
SELECT * FROM ngo_accounts WHERE email = 'ngo@example.com';
```

### NGOs not showing on frontend
Check the join query returns data:
```sql
SELECT n.ngo_id, nr.org_name 
FROM ngo_accounts n
INNER JOIN ngo_requests nr ON n.request_id = nr.request_id
WHERE nr.status = 'APPROVED';
```
