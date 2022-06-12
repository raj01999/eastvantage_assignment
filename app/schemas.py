from pydantic import BaseModel

class Address(BaseModel):
    addressLine: str 
    city: str 
    state: str
    postalCode: int