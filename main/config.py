from datetime import timedelta

class AppConfig():

    #POSTGRESQL URI
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:v4ri4nt@localhost/srhsdp"

    #SESSION SECRET KEY
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
