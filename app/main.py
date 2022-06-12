from pyexpat import model
from fastapi import Depends, FastAPI, Depends
from sqlalchemy import between
from . import schemas, models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from .getCoordinate import getCoordinate

app = FastAPI()

models.Base.metadata.create_all(engine)

def getDb():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# creating an address from request body 

@app.post("/createOneAddress")
def create_address(req: schemas.Address, db :Session = Depends(getDb)):

    # removing leading and ending extra space 
    addressLine = req.addressLine.strip()
    city = req.city.strip()
    state = req.state.strip()
    postalCode = req.postalCode

    try:
        # getting the location & coordinate data from mapquest api 
        locationData = getCoordinate(addressLine, city, state)

        newAddress = models.Address(
            addressLine = addressLine,
            city = city,
            state = state,
            country = locationData["adminArea1"],
            postalCode = postalCode,
            longitude =  locationData["latLng"]["lng"],
            latitude =  locationData["latLng"]["lat"],
            mapUrl = locationData["mapUrl"]
        )

        db.add(newAddress)
        db.commit()
        db.refresh(newAddress)

        return {
            "status": "ok",
            "data": newAddress
        }

    except Exception as e:
        print(e)
        return{
            "status":"failed",
            "msg":"Internal Server Error"
        }



# get all the address 

@app.get("/readAllAddress")
def get_all_address(db :Session = Depends(getDb)):
    try:
        allAddress = db.query(models.Address).all()
        return{
            "status" :"ok",
            "data" : allAddress
        }
    except:
        return {
            "status" : "failed",
            "msg" : "Internal Server Error"
        }


# get those address that are nearest to the request body address 

@app.get("/readNearestAddress")
def get_nearest_address(addressLine, city, state, db :Session = Depends(getDb)):
    try:
        # getting the location & coordinate data from mapquest api 
        locationData = getCoordinate(addressLine, city, state)
        quaryCoordinate = locationData["latLng"]

        someAddress1 = db.query(models.Address).filter((models.Address.latitude -  quaryCoordinate["lat"]).between(-1, 1)).all()
        someAddress2 = db.query(models.Address).filter((models.Address.longitude -  quaryCoordinate["lng"]).between(-1, 1)).all()

        someAddress = []

        """
        we know 1 degree distance = 111 km distance.
        in here the someAddress is holding all the addresses betweeen this distance :=> 156.97 Km
        sqrt(2) * 111 = 156.97 Km. 
        """

        for obj in someAddress1:
            if obj in someAddress2:
                someAddress.append(obj)

        return {
            "status": "ok",
            "data" : someAddress
        }


    except Exception as e:
        print(e)
        return{
            "status" : "failed",
            "msg" : "Internal Server Error",
        }




@app.put("/updateOneAddress/{id}")
def update_address():
    pass


@app.delete("/deleteOneAddress")
def delete_address():
    pass

