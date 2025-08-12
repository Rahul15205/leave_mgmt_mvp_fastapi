from fastapi import FastAPI, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from datetime import date, timedelta
from database import Base, engine, SessionLocal
import models, crud, schemas, auth

Base.metadata.create_all(bind=engine)


app = FastAPI(title="Leave Management System MVP")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication endpoints
@app.post("/auth/employee/login")
def employee_login(email: str = Form(...), employee_id: int = Form(...), db: Session = Depends(get_db)):
    employee = auth.authenticate_employee(db, email, employee_id)
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(employee.id), "role": "employee"}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "department": employee.department,
            "leave_balance": employee.leave_balance
        }
    }

@app.post("/auth/hr/login")
def hr_login(username: str = Form(...), password: str = Form(...)):
    hr_user = auth.authenticate_hr(username, password)
    if not hr_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(hr_user["id"]), "role": "hr"}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": hr_user
    }

# HR-only endpoints
@app.post("/employees/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_hr)):
    return crud.create_employee(db, employee)

@app.post("/leaves/{leave_id}/approve")
def approve_leave(leave_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_hr)):
    crud.approve_leave(db, leave_id)
    return {"status": "approved"}

@app.post("/leaves/{leave_id}/reject")
def reject_leave(leave_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_hr)):
    crud.reject_leave(db, leave_id)
    return {"status": "rejected"}

@app.get("/employees/")
def list_employees(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_hr)):
    return crud.get_all_employees(db)

@app.get("/leaves/")
def list_leaves(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_hr)):
    return crud.get_all_leaves(db)

@app.get("/stats")
def get_statistics(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_hr)):
    return crud.get_system_statistics(db)

# Employee-only endpoints
@app.post("/employee/leaves/", response_model=schemas.Leave)
def apply_leave_employee(leave: schemas.LeaveCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_employee)):
    # Ensure employee can only apply for their own leave
    if leave.employee_id != current_user["user"].id:
        raise HTTPException(status_code=403, detail="You can only apply for your own leave")
    return crud.apply_leave(db, leave)

@app.get("/employee/balance")
def get_my_balance(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_employee)):
    return crud.get_leave_balance(db, current_user["user"].id)

@app.get("/employee/leaves")
def get_my_leaves(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_employee)):
    return crud.get_employee_leaves(db, current_user["user"].id)

# Public endpoint for balance check (can be accessed by both roles)
@app.get("/employees/{employee_id}/balance")
def get_balance(employee_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    # HR can check anyone's balance, employees can only check their own
    if current_user["role"] == "employee" and employee_id != current_user["user"].id:
        raise HTTPException(status_code=403, detail="You can only check your own balance")
    return crud.get_leave_balance(db, employee_id)

# Mount static files after API routes to avoid conflicts
app.mount("/static", StaticFiles(directory="static"), name="static")
