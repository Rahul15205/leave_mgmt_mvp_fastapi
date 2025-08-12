from sqlalchemy.orm import Session
from datetime import timedelta
import models, schemas
from fastapi import HTTPException

def business_days_count(start_date, end_date):
    day_count = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            day_count += 1
        current += timedelta(days=1)
    return day_count

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_emp = models.Employee(**employee.dict())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def apply_leave(db: Session, leave: schemas.LeaveCreate):
    emp = db.query(models.Employee).filter(models.Employee.id == leave.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    if leave.start_date < emp.joining_date:
        raise HTTPException(status_code=400, detail="Leave before joining date")
    days = business_days_count(leave.start_date, leave.end_date)
    if days > emp.leave_balance:
        raise HTTPException(status_code=400, detail="Insufficient leave balance")
    overlap = db.query(models.Leave).filter(
        models.Leave.employee_id == leave.employee_id,
        models.Leave.status.in_(["pending", "approved"]),
        models.Leave.start_date <= leave.end_date,
        models.Leave.end_date >= leave.start_date
    ).first()
    if overlap:
        raise HTTPException(status_code=400, detail="Overlapping leave request")
    db_leave = models.Leave(employee_id=leave.employee_id, start_date=leave.start_date,
                           end_date=leave.end_date, days=days)
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

def approve_leave(db: Session, leave_id: int):
    leave = db.query(models.Leave).filter(models.Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    if leave.status != "pending":
        raise HTTPException(status_code=400, detail="Already processed")
    emp = db.query(models.Employee).filter(models.Employee.id == leave.employee_id).first()
    emp.leave_balance -= leave.days
    leave.status = "approved"
    db.commit()

def reject_leave(db: Session, leave_id: int):
    leave = db.query(models.Leave).filter(models.Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    if leave.status != "pending":
        raise HTTPException(status_code=400, detail="Already processed")
    leave.status = "rejected"
    db.commit()

def get_leave_balance(db: Session, employee_id: int):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"employee_id": emp.id, "balance": emp.leave_balance}

def get_system_statistics(db: Session):
    total_employees = db.query(models.Employee).count()
    total_leaves = db.query(models.Leave).count()
    pending_leaves = db.query(models.Leave).filter(models.Leave.status == "pending").count()
    approved_leaves = db.query(models.Leave).filter(models.Leave.status == "approved").count()
    rejected_leaves = db.query(models.Leave).filter(models.Leave.status == "rejected").count()
    
    return {
        "total_employees": total_employees,
        "total_leaves": total_leaves,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "rejected_leaves": rejected_leaves
    }

def get_all_employees(db: Session):
    employees = db.query(models.Employee).all()
    return employees

def get_all_leaves(db: Session):
    leaves = db.query(models.Leave).join(models.Employee).all()
    result = []
    for leave in leaves:
        result.append({
            "id": leave.id,
            "employee_id": leave.employee_id,
            "employee_name": leave.employee.name,
            "employee_email": leave.employee.email,
            "employee_department": leave.employee.department,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "days": leave.days,
            "status": leave.status
        })
    return result

def get_employee_leaves(db: Session, employee_id: int):
    leaves = db.query(models.Leave).filter(models.Leave.employee_id == employee_id).all()
    result = []
    for leave in leaves:
        result.append({
            "id": leave.id,
            "employee_id": leave.employee_id,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "days": leave.days,
            "status": leave.status
        })
    return result
