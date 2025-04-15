from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    calculation_type = Column(String)  # e.g., "christoffel", "riemann", "ricci"
    input_parameters = Column(JSON)
    result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 