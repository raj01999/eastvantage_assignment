from pydantic import BaseModel

# using pydanttic BaseModel creating an request model 
class Address(BaseModel):
    addressLine: str 
    city: str 
    state: str
    postalCode: int