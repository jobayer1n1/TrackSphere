from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from tracksphere.app.infrastructure.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)

    delivery = relationship("Delivery", back_populates="assignments")
    driver = relationship("Driver", back_populates="assignments")
