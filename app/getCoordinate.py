import requests

# using mapquest api for getting the coordinate of perticuller address 
coordinateApiKey = "GrqEzZehkhcuNC39yy9aWGR4CB0GLvf4"
coordinateApi = f"http://www.mapquestapi.com/geocoding/v1/address?key={coordinateApiKey}&location="

def getCoordinate(addressLine, city, state):
    mainCoordinateApi = f"{coordinateApi}{addressLine},{city},{state}"
    r = requests.get(mainCoordinateApi)
    locationData = r.json()["results"][0]["locations"][0]
    return locationData