"""
Employee API routes.
Handles all CRUD operations for employee resources.
"""

from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from app.api.deps import SessionDep
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeePublic, EmployeeUpdate
from app.core.logging import get_logger
from app.services.employee_events import publish_employee_event
from sqlmodel import select  # type: ignore

logger = get_logger(__name__)

# Create router with prefix and tags for better organization
router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    responses={404: {"description": "Employee not found"}},
)


@router.post("/", response_model=EmployeePublic, status_code=201)
async def create_employee(
    employee: EmployeeCreate, 
    session: SessionDep,
    background_tasks: BackgroundTasks
) -> Employee:
    """
    Create a new employee.

    Args:
        employee: Employee data from request body
        session: Database session (injected)
        background_tasks: Background tasks for async operations

    Returns:
        Created employee with generated ID
    """
    logger.info(f"Creating new employee: {employee.name}")
    db_employee = Employee.model_validate(employee)
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    logger.info(f"Employee created successfully with ID: {db_employee.id}")
    
    # Publish employee created event (async, non-blocking)
    background_tasks.add_task(
        publish_employee_event,
        "created",
        db_employee.id,
        db_employee.name,
        db_employee.age
    )
    
    return db_employee



@router.get("/", response_model=list[EmployeePublic])
def read_employees(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Employee]:
    """
    Retrieve a list of employees with pagination.

    Args:
        session: Database session (injected)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)

    Returns:
        List of employees
    """
    logger.info(f"Fetching employees with offset={offset}, limit={limit}")
    employees = session.exec(select(Employee).offset(offset).limit(limit)).all()
    logger.info(f"Retrieved {len(employees)} employee(s)")
    return list(employees)


@router.get("/{employee_id}", response_model=EmployeePublic)
def read_employee(employee_id: int, session: SessionDep) -> Employee:
    """
    Retrieve a single employee by ID.

    Args:
        employee_id: The ID of the employee to retrieve
        session: Database session (injected)

    Returns:
        Employee data

    Raises:
        HTTPException: 404 if employee not found
    """
    logger.info(f"Fetching employee with ID: {employee_id}")
    employee = session.get(Employee, employee_id)
    if not employee:
        logger.warning(f"Employee with ID {employee_id} not found")
        raise HTTPException(status_code=404, detail="Employee not found")
    logger.info(f"Employee found: {employee.name}")
    return employee


@router.patch("/{employee_id}", response_model=EmployeePublic)
async def update_employee(
    employee_id: int, 
    employee: EmployeeUpdate, 
    session: SessionDep,
    background_tasks: BackgroundTasks
) -> Employee:
    """
    Update an existing employee (partial update).

    Args:
        employee_id: The ID of the employee to update
        employee: Fields to update (only provided fields will be updated)
        session: Database session (injected)
        background_tasks: Background tasks for async operations

    Returns:
        Updated employee data

    Raises:
        HTTPException: 404 if employee not found
    """
    logger.info(f"Attempting to update employee with ID: {employee_id}")
    employee_db = session.get(Employee, employee_id)
    if not employee_db:
        logger.warning(f"Employee with ID {employee_id} not found for update")
        raise HTTPException(status_code=404, detail="Employee not found")

    employee_data = employee.model_dump(exclude_unset=True)
    logger.info(f"Updating employee {employee_id} with data: {employee_data}")
    employee_db = employee_db.sqlmodel_update(employee_data)
    session.add(employee_db)
    session.commit()
    session.refresh(employee_db)
    logger.info(f"Employee with ID {employee_id} updated successfully")
    
    # Publish employee updated event (async, non-blocking)
    background_tasks.add_task(
        publish_employee_event,
        "updated",
        employee_db.id,
        employee_db.name,
        employee_db.age
    )
    
    return employee_db


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int, 
    session: SessionDep,
    background_tasks: BackgroundTasks
) -> dict:
    """
    Delete an employee.

    Args:
        employee_id: The ID of the employee to delete
        session: Database session (injected)
        background_tasks: Background tasks for async operations

    Returns:
        Success confirmation

    Raises:
        HTTPException: 404 if employee not found
    """
    logger.info(f"Attempting to delete employee with ID: {employee_id}")
    employee = session.get(Employee, employee_id)
    if not employee:
        logger.warning(f"Employee with ID {employee_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Capture data before deletion for event
    employee_name = employee.name
    employee_age = employee.age
    
    session.delete(employee)
    session.commit()
    logger.info(f"Employee with ID {employee_id} deleted successfully")
    
    # Publish employee deleted event (async, non-blocking)
    background_tasks.add_task(
        publish_employee_event,
        "deleted",
        employee_id,
        employee_name,
        employee_age
    )
    
    return {"ok": True}
