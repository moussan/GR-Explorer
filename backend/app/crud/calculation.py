from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate

def get_calculation(db: Session, calculation_id: int) -> Optional[Calculation]:
    return db.query(Calculation).filter(Calculation.id == calculation_id).first()

def get_calculations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    metric_name: Optional[str] = None,
    calculation_type: Optional[str] = None
) -> List[Calculation]:
    query = db.query(Calculation)
    
    if metric_name:
        query = query.filter(Calculation.metric_name == metric_name)
    if calculation_type:
        query = query.filter(Calculation.calculation_type == calculation_type)
        
    return query.offset(skip).limit(limit).all()

def create_calculation(db: Session, calculation: CalculationCreate) -> Calculation:
    db_calculation = Calculation(
        metric_name=calculation.metric_name,
        calculation_type=calculation.calculation_type,
        input_parameters=calculation.input_parameters,
        result={},  # Initialize with empty result
        created_at=datetime.utcnow()
    )
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation

def update_calculation_result(
    db: Session, 
    calculation_id: int, 
    result: dict
) -> Optional[Calculation]:
    db_calculation = get_calculation(db, calculation_id)
    if db_calculation:
        db_calculation.result = result
        db_calculation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_calculation)
    return db_calculation

def delete_calculation(db: Session, calculation_id: int) -> bool:
    db_calculation = get_calculation(db, calculation_id)
    if db_calculation:
        db.delete(db_calculation)
        db.commit()
        return True
    return False 