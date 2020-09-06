from flask import Flask,render_template,request
from geopy.geocoders import Nominatim
from math import sin, cos, sqrt, atan2, radians
import requests
from email.mime.text import MIMEText
import smtplib

app = Flask(__name__)

class Data():
    def __init__(self,first,second,email,units):
        self.first=first
        self.second=second
        self.email=email
        self.units=units
    def addressToCoords(self, address):
        geolocator = Nominatim(user_agent="myGeocoder")
        location = geolocator.geocode(address)
        print(location.latitude)
        return (location.latitude, location.longitude)
    def distFromCoord(self,first_coord,second_coord):
        R = 6373.0
        lat1 = radians(self.first_coord[0])
        lon1 = radians(self.first_coord[1])
        lat2 = radians(self.second_coord[0])
        lon2 = radians(self.second_coord[1])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance
    def tempFromCoord(self,first_coord,second_coord):
        url = "https://climacell-microweather-v1.p.rapidapi.com/weather/realtime"
        headers = {
            'x-rapidapi-host': "climacell-microweather-v1.p.rapidapi.com",
            'x-rapidapi-key': "d0871a36edmsh993d20e4de72726p12c7f9jsnf307c256e63e"
            }
        lat1 = self.first_coord[0]
        lon1 = self.first_coord[1]
        lat2 = self.second_coord[0]
        lon2 = self.second_coord[1]
        querystring = {"unit_system":"si","fields":"temp","lat":lat1,"lon":lon1}
        response = requests.request("GET", url, headers=headers, params=querystring)
        temp1=response.json()['temp']['value']
        querystring = {"unit_system":"si","fields":"temp","lat":lat2,"lon":lon2}
        response = requests.request("GET", url, headers=headers, params=querystring)
        temp2=response.json()['temp']['value']
        return abs(temp1-temp2)
    def sendEmail(self,email,first,second,distance,units,diff):
        from_email="tompython8@gmail.com"
        from_password="Python11"
        to_email=self.email
        subject="GEOCODER 9000 - data"
        message="Distance from {} to {}: {} {}.<br>Temp difference: {}°C".format(self.first,self.second,self.distance,self.units,self.diff)
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
        try:
            data=Data(request.form["first"],request.form["second"],request.form["mail"],request.form['units'])
        except KeyError:
            return render_template("index.html", warning = 'Please select units')

        try:
            data.first_coord = data.addressToCoords(data.first)
            data.second_coord = data.addressToCoords(data.second)
        except AttributeError:
            return render_template("index.html", warning = 'Invalid address!')
        data.distance = data.distFromCoord(data.first_coord,data.second_coord)
        # changes value based on users choice
        if data.units == 'mi':
            data.distance/=1.609 # 1 mile = 1.609 kilometers
        elif data.units == 'Football fields':
            data.distance/=0.09 # 1 footbal field = 90 meters
        data.distance=round(data.distance,1)
        data.diff=round(data.tempFromCoord(data.first_coord,data.second_coord),1) # temperature difference
        data.sendEmail(data.email,data.first,data.second,data.distance,data.units,data.diff)
        if data.diff < 0:
            hiLow='lower'
        elif data.diff > 0:
            hiLow='higher'
    return render_template("success.html", first=data.first, second = data.second,distance=data.distance,units=data.units,diff=data.diff,hiLow=hiLow)

if __name__=='__main__':
    app.debug=True
    app.run()
