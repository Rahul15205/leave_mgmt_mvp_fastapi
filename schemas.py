from pydantic import BaseModel, EmailStr
from datetime import date

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    department: str
    joining_date: date

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    leave_balance: int
    class Config:
        from_attributes = True

class LeaveBase(BaseModel):
    employee_id: int
    start_date: date
    end_date: date

class LeaveCreate(LeaveBase):
    pass

class Leave(LeaveBase):
    id: int
    status: str
    days: int
    class Config:
        from_attributes = True
