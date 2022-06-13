from sqlalchemy import Column, Integer, Float, String
from .database import Base


# creatiing table for database 
# Initilizing all the coulmn in database with validation 

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    addressLine = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postalCode = Column(Integer)
    longitude = Column(Float)
    latitude = Column(Float)
    mapUrl = Column(String)