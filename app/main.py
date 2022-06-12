from fastapi import Depends, FastAPI, status, Response
from sqlalchemy import between, false
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

        # after data added in database successfully 
        return {
            "status": "ok",
            "data": newAddress
        }

    except Exception as e:
        # if some error came in server 
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : e
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
        # if some error came in server 
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : e
        }






# get those address that are nearest to the request body address {156.97 km}

@app.get("/readNearestAddress", status_code=status.HTTP_200_OK)
def get_nearest_address(res: Response, addressLine, city, state, db :Session = Depends(getDb)):
    try:
        # getting the location & coordinate data from mapquest api 
        locationData = getCoordinate(addressLine, city, state)
        quaryCoordinate = locationData["latLng"]

        someAddress1 = db.query(models.Address).filter((models.Address.latitude -  quaryCoordinate["lat"]).between(-1, 1)).all()
        someAddress2 = db.query(models.Address).filter((models.Address.longitude -  quaryCoordinate["lng"]).between(-1, 1)).all()

        """
        someAddress1 is holding those address whos latitude distace are with in 1 degree
        someAddress2 is holding those address whos longitude distace are with in 1 degree
        """

        someAddress = []

        for obj in someAddress1:
            if obj in someAddress2:
                someAddress.append(obj)
        
        """
        we know 1 degree distance = 111 km distance.
        in here the someAddress is holding all the addresses betweeen this distance :=> 156.97 Km
        sqrt(2) * 111 = 156.97 Km. 
        """

        # sending the nearest address data to user
        return {
            "status": "ok",
            "data" : someAddress
        }

    except Exception as e:
        # if some error came in server 
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : e
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
        print(e)
        # if some error came is server 
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : e
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
        # if some error came in server 
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : e
        }

