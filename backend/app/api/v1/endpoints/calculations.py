from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import calculation as crud
from app.schemas.calculation import Calculation, CalculationCreate

router = APIRouter()

@router.get("/", response_model=List[Calculation])
def read_calculations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    metric_name: Optional[str] = None,
    calculation_type: Optional[str] = None
):
    """
    Retrieve calculations with optional filtering.
    """
    calculations = crud.get_calculations(
        db, 
        skip=skip, 
        limit=limit,
        metric_name=metric_name,
        calculation_type=calculation_type
    )
    return calculations

@router.post("/", response_model=Calculation)
def create_calculation(
    *,
    db: Session = Depends(deps.get_db),
    calculation_in: CalculationCreate
):
    """
    Create new calculation.
    """
    calculation = crud.create_calculation(db=db, calculation=calculation_in)
    return calculation

@router.get("/{calculation_id}", response_model=Calculation)
def read_calculation(
    calculation_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Get calculation by ID.
    """
    calculation = crud.get_calculation(db=db, calculation_id=calculation_id)
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation

@router.put("/{calculation_id}/result", response_model=Calculation)
def update_calculation_result(
    *,
    db: Session = Depends(deps.get_db),
    calculation_id: int,
    result: dict
):
    """
    Update calculation result.
    """
    calculation = crud.update_calculation_result(
        db=db, 
        calculation_id=calculation_id,
        result=result
    )
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation

@router.delete("/{calculation_id}", response_model=Calculation)
def delete_calculation(
    *,
    db: Session = Depends(deps.get_db),
    calculation_id: int,
):
    """
    Delete calculation.
    """
    calculation = crud.get_calculation(db=db, calculation_id=calculation_id)
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    if not crud.delete_calculation(db=db, calculation_id=calculation_id):
        raise HTTPException(status_code=400, detail="Error deleting calculation")
    return calculation 