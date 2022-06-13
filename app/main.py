from fastapi import Depends, FastAPI, status, Response
from . import schemas, models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from .getCoordinate import getCoordinate
from geopy.distance import geodesic

app = FastAPI()

models.Base.metadata.create_all(engine)

def getDb():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# creating an address from request body 

@app.post("/createOneAddress", status_code=status.HTTP_201_CREATED)
def create_address(req: schemas.Address, res:Response, db :Session = Depends(getDb)):
    try:
        # removing leading and ending extra space 
        addressLine = req.addressLine.strip()
        city = req.city.strip()
        state = req.state.strip()
        postalCode = req.postalCode

        # getting the location & coordinate data from mapquest api 
        locationData = getCoordinate(addressLine, city, state)

        # creaing new row for address table 
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

        # adding row to tabel
        db.add(newAddress)
        db.commit()
        db.refresh(newAddress)

        return {
            "status": "ok",
            "data": newAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# get all the address 

@app.get("/readAllAddress", status_code=status.HTTP_200_OK)
def get_all_address(res: Response, db :Session = Depends(getDb)):
    try:
        # get all the address data from  database and send to user 
        allAddress = db.query(models.Address).all()
        return{
            "status" :"ok",
            "data" : allAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# get those address that are nearest to the request body address {156.97 km}

@app.get("/readNearestAddress", status_code=status.HTTP_200_OK)
def get_nearest_address(res: Response, addressLine, city, state, db :Session = Depends(getDb)):
    try:
        # getting the location & coordinate data from mapquest api 
        locationData = getCoordinate(addressLine, city, state)
        quaryCoordinate = locationData["latLng"]

        firstCoordinate = (quaryCoordinate["lat"] , quaryCoordinate["lng"])

        allAddress = db.query(models.Address).all()

        someAddress = []

        """
        In here geodesic returning the distance between quary address and all database address,
        If the distance is below 100km than only it's save the address to someAddress list. 

        geodesic is importaed from geopy.distance module

        Here, someAddress will hold all the address that between 100km
        """

        for address in allAddress:
            secondCoordinate = (address.latitude, address.longitude)
            distanceBetween = geodesic(firstCoordinate, secondCoordinate).km
            if distanceBetween <= 100:
                someAddress.append(address)
        

        # sending the nearest address data to user
        return {
            "status": "ok",
            "data" : someAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# update the address through id and request body 

@app.put("/updateOneAddress/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_address(id, req: schemas.Address, res: Response, db: Session = Depends(getDb)):
    try:
        # removing leading and ending extra space 
        addressLine = req.addressLine.strip()
        city = req.city.strip()
        state = req.state.strip()
        postalCode = req.postalCode

        # getting the location & coordinate data from mapquest api 
        locationData = getCoordinate(addressLine, city, state)

        newAddress = {
            "addressLine" : addressLine,
            "city" : city,
            "state" : state,
            "country" : locationData["adminArea1"],
            "postalCode" : postalCode,
            "longitude" :  locationData["latLng"]["lng"],
            "latitude" :  locationData["latLng"]["lat"],
            "mapUrl" : locationData["mapUrl"]
        }

        # updating address through id and query params 
        updatedAddress = db.query(models.Address).filter(models.Address.id == id).update(newAddress)

        # if data not found in database 
        if not updatedAddress:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status" : "failed",
                "msg" : f"Address id {id} not found"
            }

        db.commit()

        # if data got sucessfully updated 
        return {
            "status" : "ok",
            "data" : updatedAddress
        }
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# delete the address through id 

@app.delete("/deleteOneAddress/{id}", status_code=status.HTTP_202_ACCEPTED)
def delete_address(id, res: Response, db: Session = Depends(getDb) ):
    try:
        # deleting address from databse through id
        deletedAddress = db.query(models.Address).filter(models.Address.id == id).delete(synchronize_session=False)

        # if data not found in database 
        if not deletedAddress:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status" : "failed",
                "msg" : f"Address id {id} not found"
            }
        
        db.commit()

        # if data got sucessfully deleted 
        return {
            "status" : "ok",
            "data" : deletedAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }
