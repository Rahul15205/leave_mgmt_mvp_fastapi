# Leave Management System - High Level Design (Enhanced)

##High Level System Design

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Landing Portal │  │ Employee Portal │  │  HR Admin Portal│ │
│  │   (index.html)  │  │(employee.html)  │  │   (hr.html)     │ │
│  │                 │  │                 │  │                 │ │
│  │ • Portal Select │  │ • Self Service  │  │ • Employee Mgmt │ │
│  │ • Auth Info     │  │ • Leave Apply   │  │ • Leave Approval│ │
│  │ • Responsive UI │  │ • Leave History │  │ • Statistics    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────┬───────────────────┬───────────────────┬───────┘
                  │                   │                   │
                  │ JWT Auth + REST API Calls             │
                  ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AUTHENTICATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   auth.py       │  │  JWT Tokens     │  │ Role-Based      │ │
│  │                 │  │                 │  │ Access Control  │ │
│  │ • Employee Auth │  │ • Token Create  │  │                 │ │
│  │ • HR Auth       │  │ • Token Verify  │  │ • Employee Role │ │
│  │ • Password Hash │  │ • Token Expire  │  │ • HR Role       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Authenticated Requests
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Application Server                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   main.py   │  │ schemas.py  │  │   crud.py   │            │
│  │ (Endpoints) │  │(Validation) │  │(Business    │            │
│  │             │  │             │  │ Logic)      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                │
│  Role-Based Endpoints:                                         │
│  • /auth/employee/login  • /auth/hr/login                     │
│  • /employee/leaves/     • /employees/ (HR only)             │
│  • /employee/balance     • /leaves/ (HR only)                │
│  • /employee/leaves      • /leaves/{id}/approve (HR only)    │
│  • JWT Token Validation • /stats (HR only)                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │ SQLAlchemy ORM + Business Logic
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  SQLite Database (Current) / PostgreSQL (Future)              │
│                                                                │
│  ┌─────────────────┐         ┌─────────────────┐              │
│  │   EMPLOYEES     │         │     LEAVES      │              │
│  │─────────────────│         │─────────────────│              │
│  │ id (PK)         │◄────────┤ id (PK)         │              │
│  │ name            │         │ employee_id (FK)│              │
│  │ email (UNIQUE)  │         │ start_date      │              │
│  │ department      │         │ end_date        │              │
│  │ joining_date    │         │ status          │              │
│  │ leave_balance   │         │ days            │              │
│  └─────────────────┘         └─────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLASS DIAGRAM                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│      Employee       │         │       Leave         │
├─────────────────────┤         ├─────────────────────┤
│ - id: int           │         │ - id: int           │
│ - name: str         │         │ - employee_id: int  │
│ - email: str        │◄────────┤ - start_date: date  │
│ - department: str   │   1:N   │ - end_date: date    │
│ - joining_date: date│         │ - status: str       │
│ - leave_balance: int│         │ - days: int         │
├─────────────────────┤         ├─────────────────────┤
│ + get_balance()     │         │ + calculate_days()  │
│ + deduct_balance()  │         │ + approve()         │
│ + add_balance()     │         │ + reject()          │
└─────────────────────┘         │ + is_overlapping()  │
                                └─────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│    AuthService      │         │     CRUDService     │
├─────────────────────┤         ├─────────────────────┤
│ - secret_key: str   │         │ - db: Session       │
│ - algorithm: str    │         ├─────────────────────┤
├─────────────────────┤         │ + create_employee() │
│ + create_token()    │         │ + get_employee()    │
│ + verify_token()    │         │ + apply_leave()     │
│ + hash_password()   │         │ + approve_leave()   │
│ + verify_password() │         │ + reject_leave()    │
│ + authenticate_emp()│         │ + get_balance()     │
│ + authenticate_hr() │         │ + business_days()   │
└─────────────────────┘         └─────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│   EmployeePortal    │         │    HRAdminPortal    │
├─────────────────────┤         ├─────────────────────┤
│ - current_user      │         │ - admin_user        │
│ - auth_token        │         │ - auth_token        │
├─────────────────────┤         ├─────────────────────┤
│ + login()           │         │ + login()           │
│ + apply_leave()     │         │ + create_employee() │
│ + view_history()    │         │ + view_all_leaves() │
│ + check_balance()   │         │ + approve_leave()   │
│ + logout()          │         │ + reject_leave()    │
└─────────────────────┘         │ + view_statistics() │
                                │ + export_data()     │
                                └─────────────────────┘
```

## Sequence Diagrams

### Employee Leave Application Flow
```
Employee Portal    Auth Service    FastAPI Server    Database    HR Portal
      │                 │               │             │            │
      │──── login() ────►│               │             │            │
      │◄─── JWT token ──│               │             │            │
      │                 │               │             │            │
      │──── apply_leave() ──────────────►│             │            │
      │                 │               │──── save ──►│            │
      │                 │               │◄─── ok ────│            │
      │◄──── success ──────────────────│             │            │
      │                 │               │             │            │
      │                 │               │──── notify ────────────►│
      │                 │               │             │            │
```

### HR Approval Flow
```
HR Portal      Auth Service    FastAPI Server    Database    Employee Portal
    │               │               │             │               │
    │─── login() ───►│               │             │               │
    │◄── JWT token ─│               │             │               │
    │               │               │             │               │
    │─── approve_leave() ───────────►│             │               │
    │               │               │─── update ─►│               │
    │               │               │─── deduct ─►│               │
    │               │               │◄─── ok ────│               │
    │◄─── success ─────────────────│             │               │
    │               │               │             │               │
    │               │               │──── notify ────────────────►│
```

## Pseudocode for Core Functions

### Employee Authentication
```python
def authenticate_employee(db, email, employee_id):
    """
    Authenticate employee using email and employee ID
    """
    employee = db.query(Employee).filter(
        Employee.email == email,
        Employee.id == employee_id
    ).first()
    
    if employee:
        return employee
    return None

def create_access_token(data, expires_delta):
    """
    Create JWT access token with expiration
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### Leave Application Logic
```python
def apply_leave(db, leave_request):
    """
    Apply for leave with comprehensive validation
    """
    # Step 1: Validate employee exists
    employee = get_employee(db, leave_request.employee_id)
    if not employee:
        raise HTTPException(404, "Employee not found")
    
    # Step 2: Validate leave start date
    if leave_request.start_date < employee.joining_date:
        raise HTTPException(400, "Leave before joining date")
    
    # Step 3: Calculate business days
    days = calculate_business_days(
        leave_request.start_date, 
        leave_request.end_date
    )
    
    # Step 4: Check leave balance
    if days > employee.leave_balance:
        raise HTTPException(400, "Insufficient leave balance")
    
    # Step 5: Check for overlapping requests
    overlapping = check_overlapping_leaves(db, leave_request)
    if overlapping:
        raise HTTPException(400, "Overlapping leave request")
    
    # Step 6: Create leave record
    leave = Leave(
        employee_id=leave_request.employee_id,
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        days=days,
        status="pending"
    )
    
    db.add(leave)
    db.commit()
    return leave

def calculate_business_days(start_date, end_date):
    """
    Calculate business days excluding weekends
    """
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Monday = 0, Sunday = 6
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days

def check_overlapping_leaves(db, leave_request):
    """
    Check for overlapping leave requests
    """
    overlapping = db.query(Leave).filter(
        Leave.employee_id == leave_request.employee_id,
        Leave.status.in_(["pending", "approved"]),
        Leave.start_date <= leave_request.end_date,
        Leave.end_date >= leave_request.start_date
    ).first()
    
    return overlapping is not None
```

### Leave Approval Logic
```python
def approve_leave(db, leave_id):
    """
    Approve leave and deduct from balance
    """
    # Step 1: Get leave request
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(404, "Leave request not found")
    
    # Step 2: Check if already processed
    if leave.status != "pending":
        raise HTTPException(400, "Leave already processed")
    
    # Step 3: Get employee and check balance
    employee = db.query(Employee).filter(
        Employee.id == leave.employee_id
    ).first()
    
    if employee.leave_balance < leave.days:
        raise HTTPException(400, "Insufficient leave balance")
    
    # Step 4: Update leave status and employee balance
    leave.status = "approved"
    employee.leave_balance -= leave.days
    
    db.commit()
    return leave

def reject_leave(db, leave_id):
    """
    Reject leave request (no balance deduction)
    """
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(404, "Leave request not found")
    
    if leave.status != "pending":
        raise HTTPException(400, "Leave already processed")
    
    leave.status = "rejected"
    db.commit()
    return leave
```

### Role-Based Access Control
```python
def get_current_user(token: str, required_role: str = None):
    """
    Validate JWT token and check role permissions
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None:
            raise HTTPException(401, "Invalid token")
        
        if required_role and role != required_role:
            raise HTTPException(403, "Insufficient permissions")
        
        return {"id": user_id, "role": role}
    
    except JWTError:
        raise HTTPException(401, "Invalid token")

# Dependency for HR-only endpoints
def get_current_hr_user(token: str = Depends(oauth2_scheme)):
    return get_current_user(token, required_role="hr")

# Dependency for Employee-only endpoints  
def get_current_employee(token: str = Depends(oauth2_scheme)):
    return get_current_user(token, required_role="employee")
```

## API Flow Diagram

```
┌─────────────┐    HTTP Request    ┌─────────────┐    ORM Query    ┌─────────────┐
│   Client    │ ──────────────────► │  FastAPI    │ ──────────────► │  Database   │
│ (Browser/   │                    │ Application │                 │  (SQLite)   │
│  Mobile)    │ ◄────────────────── │   Server    │ ◄────────────── │             │
└─────────────┘    JSON Response   └─────────────┘   Query Result  └─────────────┘
                                           │
                                           ▼
                                   ┌─────────────┐
                                   │ Business    │
                                   │ Logic &     │
                                   │ Validation  │
                                   │ (crud.py)   │
                                   └─────────────┘
```

## Scaling Strategy: 50 → 500 Employees

### Current Architecture (50 employees)
- **Single FastAPI instance**
- **SQLite database**
- **Basic HTML frontend**
- **No caching**

### Scaled Architecture (500 employees)

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │   (Nginx/ALB)   │
                    └─────────┬───────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  FastAPI    │   │  FastAPI    │   │  FastAPI    │
    │ Instance 1  │   │ Instance 2  │   │ Instance 3  │
    └─────────────┘   └─────────────┘   └─────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
                    ┌─────────────────┐
                    │ Redis Cache     │
                    │ (Session Store) │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ PostgreSQL      │
                    │ (Primary DB)    │
                    │ + Read Replicas │
                    └─────────────────┘
```

### Scaling Components

#### 1. **Application Layer**
- **Horizontal Scaling**: Multiple FastAPI instances
- **Load Balancing**: Nginx or AWS ALB
- **Containerization**: Docker + Kubernetes
- **Auto-scaling**: Based on CPU/memory usage

#### 2. **Database Layer**
- **Migration**: SQLite → PostgreSQL
- **Read Replicas**: For balance queries
- **Connection Pooling**: PgBouncer
- **Database Indexing**: On frequently queried fields

#### 3. **Caching Layer**
- **Redis**: Session management, frequently accessed data
- **Application Cache**: Employee data, leave policies
- **CDN**: Static assets

#### 4. **Additional Services**
- **Message Queue**: Celery + Redis for async tasks
- **Email Service**: SendGrid/SES for notifications
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## Database Design Considerations

### Current Schema
```sql
-- Employees Table
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    joining_date DATE NOT NULL,
    leave_balance INTEGER DEFAULT 20
);

-- Leaves Table  
CREATE TABLE leaves (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    days INTEGER NOT NULL
);
```

### Optimizations for Scale
```sql
-- Add indexes for performance
CREATE INDEX idx_employee_email ON employees(email);
CREATE INDEX idx_employee_department ON employees(department);
CREATE INDEX idx_leave_employee_id ON leaves(employee_id);
CREATE INDEX idx_leave_status ON leaves(status);
CREATE INDEX idx_leave_dates ON leaves(start_date, end_date);

-- Add constraints
ALTER TABLE leaves ADD CONSTRAINT chk_dates CHECK (end_date >= start_date);
ALTER TABLE leaves ADD CONSTRAINT chk_status CHECK (status IN ('pending', 'approved', 'rejected'));
```

## Security Considerations

### Current (MVP)
- Basic input validation
- SQL injection protection (ORM)

### Production Ready
- **Authentication**: JWT tokens
- **Authorization**: Role-based access (HR, Employee, Manager)
- **HTTPS**: SSL/TLS encryption
- **Rate Limiting**: API throttling
- **Input Sanitization**: XSS protection
- **Audit Logging**: Track all changes

## Deployment Architecture

### Current: Single Server
```
┌─────────────────┐
│   Single VM     │
│ ┌─────────────┐ │
│ │  FastAPI    │ │
│ │    App      │ │
│ └─────────────┘ │
│ ┌─────────────┐ │
│ │  SQLite DB  │ │
│ └─────────────┘ │
└─────────────────┘
```

### Scaled: Microservices
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Employee       │  │  Leave          │  │  Notification   │
│  Service        │  │  Service        │  │  Service        │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │
│ │  FastAPI    │ │  │ │  FastAPI    │ │  │ │  FastAPI    │ │
│ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │
│ │ Employee DB │ │  │ │  Leave DB   │ │  │ │ Message     │ │
│ └─────────────┘ │  │ └─────────────┘ │  │ │ Queue       │ │
└─────────────────┘  └─────────────────┘  │ └─────────────┘ │
                                          └─────────────────┘
```

## Performance Metrics

### Target SLAs (500 employees)
- **Response Time**: < 200ms for 95% of requests
- **Availability**: 99.9% uptime
- **Throughput**: 1000 requests/minute
- **Concurrent Users**: 100 simultaneous users

### Monitoring KPIs
- API response times
- Database query performance
- Error rates
- User activity patterns
- Leave approval bottlenecks
