# Leave Management System

## Overview
A comprehensive FastAPI-based Leave Management System designed for a startup with 50 employees. The system provides role-based access control with separate Employee and HR portals, enabling efficient leave management with modern authentication and professional user interfaces.

## Features

### Core Features
- ✅ **Employee Management**: Add employees with complete details (Name, Email, Department, Joining Date)
- ✅ **Leave Application**: Apply for leave requests with date validation
- ✅ **Leave Approval Workflow**: Approve/Reject leave requests with proper authorization
- ✅ **Leave Balance Tracking**: Real-time balance updates and tracking
- ✅ **Business Days Calculation**: Automatic calculation excluding weekends
- ✅ **Edge Case Handling**: Comprehensive validation and error handling

### Enhanced Features
- ✅ **Role-Based Authentication**: JWT-based secure authentication system
- ✅ **Employee Portal**: Self-service portal for employees to manage their leave
- ✅ **HR Admin Portal**: Administrative dashboard for HR management
- ✅ **Real-time Statistics**: Live dashboard with system metrics
- ✅ **Professional UI**: Modern, responsive user interface
- ✅ **Data Export**: Export functionality for system data

## Setup Instructions

### Prerequisites
- **Python 3.8+** (Recommended: Python 3.9 or higher)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### Step-by-Step Installation

#### 1. Clone/Download the Project
```bash
git clone <repository-url>
cd leave_mgmt_mvp_fastapi
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Database Setup
The application uses SQLite and automatically creates the database on first run. No manual database setup required.

#### 5. Start the Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 6. Access the System
- **🏠 Main Portal**: http://localhost:8000/static/index.html
- **👤 Employee Portal**: http://localhost:8000/static/employee.html
- **👨‍💼 HR Admin Portal**: http://localhost:8000/static/hr.html
- **📖 API Documentation**: http://localhost:8000/docs
- **📋 Alternative Docs**: http://localhost:8000/redoc

### Authentication Credentials

#### Employee Login
- **Method**: Use employee email + employee ID
- **Example**: After adding an employee, use their email and ID from the database

#### HR Admin Login
- **Username**: `hr@company.com`
- **Password**: `hr123`

### Quick Start Guide

1. **Start the server** using the command above
2. **Open** http://localhost:8000/static/index.html
3. **Login as HR** to add employees and manage the system
4. **Login as Employee** to apply for leave and view requests
5. **Test the system** using the provided test script: `test_api.ps1`

## API Endpoints

### Authentication Endpoints

#### Employee Login
- **POST** `/auth/employee/login`
- **Body** (Form Data):
  ```
  email=employee@company.com&employee_id=1
  ```
- **Response**: JWT token + user details

#### HR Login
- **POST** `/auth/hr/login`
- **Body** (Form Data):
  ```
  username=hr@company.com&password=hr123
  ```
- **Response**: JWT token + user details

### HR-Only Endpoints (Requires HR Authentication)

#### 1. Create Employee
- **POST** `/employees/`
- **Headers**: `Authorization: Bearer <hr_jwt_token>`
- **Body**: 
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering", 
    "joining_date": "2024-01-15"
  }
  ```

#### 2. Get All Employees
- **GET** `/employees/`
- **Headers**: `Authorization: Bearer <hr_jwt_token>`

#### 3. Get All Leave Requests
- **GET** `/leaves/`
- **Headers**: `Authorization: Bearer <hr_jwt_token>`

#### 4. Approve Leave
- **POST** `/leaves/{leave_id}/approve`
- **Headers**: `Authorization: Bearer <hr_jwt_token>`

#### 5. Reject Leave  
- **POST** `/leaves/{leave_id}/reject`
- **Headers**: `Authorization: Bearer <hr_jwt_token>`

#### 6. Get System Statistics
- **GET** `/stats`
- **Headers**: `Authorization: Bearer <hr_jwt_token>`

### Employee-Only Endpoints (Requires Employee Authentication)

#### 1. Apply for Leave
- **POST** `/employee/leaves/`
- **Headers**: `Authorization: Bearer <employee_jwt_token>`
- **Body**:
  ```json
  {
    "employee_id": 1,
    "start_date": "2024-08-15",
    "end_date": "2024-08-17"
  }
  ```

#### 2. Get Own Leave Requests
- **GET** `/employee/leaves`
- **Headers**: `Authorization: Bearer <employee_jwt_token>`

#### 3. Get Own Leave Balance
- **GET** `/employee/balance`
- **Headers**: `Authorization: Bearer <employee_jwt_token>`

### Shared Endpoints (Both Roles)

#### Get Employee Balance
- **GET** `/employees/{employee_id}/balance`
- **Headers**: `Authorization: Bearer <jwt_token>`
- **Note**: Employees can only access their own balance

## Edge Cases Handled

### Core Business Logic Edge Cases
1. **Leave before joining date**: System validates that leave start date cannot be before employee's joining date
2. **Insufficient leave balance**: Validates that requested leave days do not exceed available balance
3. **Overlapping leave requests**: Prevents conflicting leave periods for the same employee (pending/approved leaves)
4. **Employee not found**: Returns proper 404 error for invalid employee IDs
5. **Invalid date ranges**: Ensures end date is not before start date
6. **Business days calculation**: Leave calculation automatically excludes weekends (Saturday/Sunday)
7. **Duplicate processing**: Prevents re-approving or re-rejecting already processed leave requests

### Authentication & Authorization Edge Cases
8. **Invalid JWT tokens**: Proper handling of expired or malformed tokens
9. **Role-based access violations**: Employees cannot access HR-only endpoints and vice versa
10. **Cross-employee data access**: Employees can only view/modify their own leave data
11. **Unauthorized API access**: All protected endpoints require valid authentication

### Data Validation Edge Cases
12. **Invalid email formats**: Email validation during employee creation
13. **Duplicate employee emails**: Prevents creating employees with existing email addresses
14. **Invalid employee IDs**: Handles non-existent employee ID references
15. **Malformed request data**: Proper validation of all input parameters
16. **Future date validation**: Prevents applying for leave with past dates

### System Robustness Edge Cases
17. **Database connection errors**: Graceful error handling for database issues
18. **Concurrent request handling**: Thread-safe operations for simultaneous requests
19. **Form data validation**: Proper handling of login form submissions
20. **Empty or null values**: Validation for required fields and data integrity

## Database Schema

### Employee Table
- id (Primary Key)
- name
- email (Unique)
- department
- joining_date
- leave_balance (Default: 20 days)

### Leave Table
- id (Primary Key)
- employee_id (Foreign Key)
- start_date
- end_date
- status (pending/approved/rejected)
- days (calculated business days)

## Assumptions

### Business Logic Assumptions
1. **Default Leave Balance**: Each employee starts with 20 days of annual leave
2. **Business Days Only**: Leave calculation considers only Monday-Friday as working days
3. **Single Leave Type**: System handles general leave (no categorization into sick/casual/vacation)
4. **Annual Leave Policy**: Leave balance doesn't automatically reset annually (MVP scope limitation)
5. **Single-Level Approval**: HR can directly approve/reject without multi-level workflow
6. **Leave Deduction**: Leave balance is deducted only upon approval, not upon application

### Authentication & Security Assumptions
7. **HR Admin Account**: Single hardcoded HR admin for MVP (`hr@company.com` / `hr123`)
8. **Employee Authentication**: Employees authenticate using email + employee ID combination
9. **JWT Token Expiry**: Tokens expire after a reasonable time period (configurable)
10. **Password Security**: HR password is hashed using bcrypt for security
11. **Role-Based Access**: Strict separation between employee and HR functionalities

### Technical Assumptions
12. **SQLite Database**: Suitable for MVP with 50 employees (production may need PostgreSQL)
13. **Single Server Instance**: No load balancing or clustering required for MVP
14. **Local File Storage**: Database and static files stored locally
15. **No External Integrations**: Self-contained system without third-party API dependencies
16. **Browser Compatibility**: Modern browsers with JavaScript enabled

### Data & Workflow Assumptions
17. **Employee Data Integrity**: Email addresses are unique identifiers for employees
18. **Leave Request Workflow**: Employees can only apply for their own leave
19. **Date Handling**: All dates are handled in ISO format (YYYY-MM-DD)
20. **Timezone**: System assumes single timezone operation (no multi-timezone support)
21. **Data Persistence**: All data persists in SQLite database with proper relationships

## Potential Improvements

### Immediate Enhancements (Phase 1)
- **Leave Type Categories**: Implement sick leave, casual leave, vacation leave with separate balances
- **Email Notifications**: Send notifications for leave applications, approvals, and rejections
- **Leave Modification**: Allow employees to modify pending leave requests
- **Leave Cancellation**: Enable cancellation of approved future leaves
- **Advanced Search**: Search and filter employees and leave requests
- **Bulk Operations**: Bulk approve/reject multiple leave requests
- **Leave History Export**: Export individual employee leave history

### Security & Authentication Improvements (Phase 2)
- **Multi-Factor Authentication (MFA)**: Add 2FA for enhanced security
- **Password Policies**: Implement strong password requirements
- **Session Management**: Advanced session handling and timeout controls
- **Audit Logging**: Track all system actions for compliance
- **Role Management**: Dynamic role assignment and permissions
- **OAuth Integration**: Support for Google/Microsoft SSO
- **API Rate Limiting**: Prevent abuse with request throttling

### Business Logic Enhancements (Phase 3)
- **Multi-Level Approval**: Implement manager → HR approval workflow
- **Leave Policies**: Configurable leave policies per department/role
- **Public Holiday Integration**: Automatic exclusion of public holidays
- **Leave Accrual**: Monthly/quarterly leave balance accrual system
- **Carry Forward Rules**: Handle unused leave balance rollover
- **Probation Period**: Different leave policies for probationary employees
- **Leave Calendar**: Visual calendar view of team leave schedules

### User Experience Improvements (Phase 4)
- **Mobile Responsive**: Enhanced mobile interface
- **Progressive Web App (PWA)**: Offline capability and app-like experience
- **Real-time Notifications**: WebSocket-based live notifications
- **Dashboard Analytics**: Advanced reporting and analytics
- **Team Calendar**: View team leave schedules and availability
- **Leave Balance Forecasting**: Predict future leave balance
- **Automated Reminders**: Remind about pending approvals and leave balances

### Technical & Scalability Improvements (Phase 5)
- **Database Migration**: PostgreSQL for production scalability
- **Microservices Architecture**: Separate services for auth, leave, notifications
- **Containerization**: Docker deployment with Kubernetes orchestration
- **Caching Layer**: Redis for improved performance
- **Load Balancing**: Handle increased traffic with multiple server instances
- **Database Optimization**: Indexing, query optimization, and connection pooling
- **API Versioning**: Support multiple API versions for backward compatibility
- **Monitoring & Logging**: Comprehensive system monitoring and alerting

### Integration & External Systems (Phase 6)
- **HRMS Integration**: Connect with existing HR management systems
- **Payroll Integration**: Sync leave data with payroll systems
- **Calendar Integration**: Sync with Google Calendar, Outlook
- **Slack/Teams Integration**: Leave notifications and approvals via chat
- **Time Tracking Integration**: Connect with time tracking tools
- **Reporting Tools**: Integration with BI tools for advanced analytics
- **Backup & Recovery**: Automated backup and disaster recovery systems

## Testing

### Automated Testing Script
The system includes a comprehensive PowerShell test script:
```bash
# Run all API tests
.\test_api.ps1
```

### Manual Testing Options

#### 1. Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### 2. Web Interface Testing
1. **HR Portal Testing**:
   - Navigate to http://localhost:8000/static/hr.html
   - Login with `hr@company.com` / `hr123`
   - Test employee creation, leave management, and statistics

2. **Employee Portal Testing**:
   - Navigate to http://localhost:8000/static/employee.html
   - Login with employee email and ID (after creating employee via HR portal)
   - Test leave application and history viewing

#### 3. API Testing with cURL
```bash
# 1. HR Login
curl -X POST "http://localhost:8000/auth/hr/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr@company.com&password=hr123"

# 2. Create Employee (use JWT token from login)
curl -X POST "http://localhost:8000/employees/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <hr_jwt_token>" \
  -d '{"name":"John Doe","email":"john@example.com","department":"Engineering","joining_date":"2024-01-15"}'

# 3. Employee Login
curl -X POST "http://localhost:8000/auth/employee/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=john@example.com&employee_id=1"

# 4. Apply for Leave (use employee JWT token)
curl -X POST "http://localhost:8000/employee/leaves/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <employee_jwt_token>" \
  -d '{"employee_id":1,"start_date":"2024-08-15","end_date":"2024-08-17"}'
```

## Technology Stack

### Backend Technologies
- **Framework**: FastAPI (Modern, fast web framework for building APIs)
- **Database**: SQLite (Development) + SQLAlchemy ORM (Object-Relational Mapping)
- **Authentication**: JWT (JSON Web Tokens) with python-jose
- **Password Hashing**: bcrypt via passlib
- **Validation**: Pydantic (Data validation and settings management)
- **Server**: Uvicorn (ASGI server implementation)

### Frontend Technologies
- **UI Framework**: Vanilla HTML5/CSS3/JavaScript
- **Styling**: Modern CSS with Flexbox/Grid layouts
- **Icons**: Font Awesome 6.0
- **Responsive Design**: Mobile-first approach
- **Authentication**: JWT token-based client-side auth

### Development Tools
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Testing**: PowerShell test scripts for API validation
- **Database Management**: SQLAlchemy migrations and schema management
- **Development Server**: Hot-reload development environment
