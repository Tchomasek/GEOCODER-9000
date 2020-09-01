from flask import Flask,render_template,request
from geopy.geocoders import Nominatim
from math import sin, cos, sqrt, atan2, radians
import requests
from email.mime.text import MIMEText
import smtplib

app = Flask(__name__)

# returns coordinates of given address
def addressToCoords(address):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    print(location.latitude)
    return (location.latitude, location.longitude)

# mathematical formula, returns distance between two given places
def distFromCoord(coord1,coord2):
    # approximate radius of earth in km
    R = 6373.0
    lat1 = radians(coord1[0])
    lon1 = radians(coord1[1])
    lat2 = radians(coord2[0])
    lon2 = radians(coord2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# returns temp at given location
def tempFromCoord(coord1,coord2):
    url = "https://climacell-microweather-v1.p.rapidapi.com/weather/realtime"
    headers = {
        'x-rapidapi-host': "climacell-microweather-v1.p.rapidapi.com",
        'x-rapidapi-key': "d0871a36edmsh993d20e4de72726p12c7f9jsnf307c256e63e"
        }
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    querystring = {"unit_system":"si","fields":"temp","lat":lat1,"lon":lon1}
    response = requests.request("GET", url, headers=headers, params=querystring)
    temp1=response.json()['temp']['value']
    querystring = {"unit_system":"si","fields":"temp","lat":lat2,"lon":lon2}
    response = requests.request("GET", url, headers=headers, params=querystring)
    temp2=response.json()['temp']['value']
    return temp1-temp2

# arguments: recipient, first address, second address, distance between places, temp difference
def sendEmail(email,first,second,distance,units,diff):
    from_email="tompython8@gmail.com"
    from_password="Python11"
    to_email=email
    subject="GEOCODER 9000 - data"
    message="Distance from {} to {}: {} {}.<br>Temp difference: {}°C".format(first,second,distance,units,diff)
    msg=MIMEText(message, 'html')
    msg['Subject']=subject
    msg['To']=to_email
    msg['From']=from_email
    gmail=smtplib.SMTP('smtp.gmail.com',587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email, from_password)
    gmail.send_message(msg)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success",methods=['POST'])
def success():
    if request.method=='POST':
        first=request.form["first"] # first address
        second=request.form["second"] # second address
        mail=request.form["mail"]
        units=request.form['units']
        first_coord = addressToCoords(first)
        second_coord = addressToCoords(second)
        distance = distFromCoord(first_coord,second_coord)
        # changes value based on users choice
        if units == 'mi':
            distance/=1.609 # 1 mile = 1.609 kilometers
        elif units == 'Football fields':
            distance/=0.09 # 1 footbal field = 90 meters
        distance=round(distance,1)
        diff=round(tempFromCoord(first_coord,second_coord),1) # temperature difference
        sendEmail(mail,first,second,distance,units,diff)
        # decides
        if diff < 0:
            hiLow='lower'
        elif diff > 0:
            hiLow='higher'
    return render_template("success.html", first=first, second = second,distance=distance,units=units,diff=abs(diff),hiLow=hiLow)

if __name__=='__main__':
    app.debug=True
    app.run()
