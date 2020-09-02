# geo
geolocator web app

This is my little fun project. User gives two addresses, his email and chooses units, in which result should be calculated. 
After submiting, the distance between those two places and temperature difference is displayed and sent to the given email.
App uses API that allows only 100 free querys per day and one run of the app uses two of those. This means that maximum of 50 runs is allowed per day.

App is also daployed on Heroku. 
https://geocoder9000.herokuapp.com/

NOTES:

App returns an error when nonsensical address or email is given, or units are not selected. Returning relevant message for those cases will be my next step.

Added file appOOP.py, where i tried to demonstrate my ability to use classes.
