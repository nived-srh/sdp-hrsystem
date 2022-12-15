from datetime import timedelta
import os

class AppConfig():

    MODE = "DEV"

    if MODE == "DEV":
        #POSTGRESQL URI
        SQLALCHEMY_DATABASE_URI = "postgresql://postgres:v4ri4nt@localhost/srhsdp"
        #SESSION SECRET KEY
        SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
        PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)

        #DEFAULT CREDS
        DFLT_PASSWORD = 'qwerty1234'
    elif MODE == "PROD":
        #POSTGRESQL URI
        SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI") #"postgresql://nivedsdp:AGNUSWgGoZ74UpmPu3OF7njqsjVwBj6U@dpg-ce365msgqg43k3jg08jg-a.frankfurt-postgres.render.com/sdp"
        #SESSION SECRET KEY
        SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
        PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)

        #DEFAULT CREDS
        DFLT_PASSWORD = 'qwerty1234'

