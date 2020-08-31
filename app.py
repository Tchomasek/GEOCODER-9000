from flask import Flask,render_template,request

app = Flask(__name__)

def addressToCoords(address):
    from geopy.geocoders import Nominatim

    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude)

def dist_from_coord(coord1,coord2):
    from math import sin, cos, sqrt, atan2, radians

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

def temp_from_coord(coord1,coord2):
    import requests

    url = "https://climacell-microweather-v1.p.rapidapi.com/weather/realtime"
    headers = {
        'x-rapidapi-host': "climacell-microweather-v1.p.rapidapi.com",
        'x-rapidapi-key': "d0871a36edmsh993d20e4de72726p12c7f9jsnf307c256e63e"
        }

    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]

    print(lat1,lon1,lat2,lon2)

    querystring = {"unit_system":"si","fields":"temp","lat":lat1,"lon":lon1}
    response = requests.request("GET", url, headers=headers, params=querystring)
    temp1=response.json()['temp']['value']
    print(temp1)
    querystring = {"unit_system":"si","fields":"temp","lat":lat2,"lon":lon2}
    response = requests.request("GET", url, headers=headers, params=querystring)
    temp2=response.json()['temp']['value']
    print(temp2)
    return temp1-temp2

def send_email(email,first,second,distance,units,diff):
    from email.mime.text import MIMEText
    import smtplib

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
        first=request.form["first"]
        second=request.form["second"]
        mail=request.form["mail"]
        units=request.form['units']

        first_coord = addressToCoords(first)
        second_coord = addressToCoords(second)

        distance = dist_from_coord(first_coord,second_coord)

        if units == 'mi':
            distance/=1.609
        elif units == 'Football fields':
            distance/=0.09
        distance=round(distance,1)
        diff=round(temp_from_coord(first_coord,second_coord),1)
        send_email(mail,first,second,distance,units,diff)
        if diff < 0:
            hiLow='lower'
        elif diff > 0:
            hiLow='higher'

    return render_template("success.html", first=first, second = second,distance=distance,units=units,diff=diff,hiLow=hiLow)

if __name__=='__main__':
    app.debug=True
    app.run()
