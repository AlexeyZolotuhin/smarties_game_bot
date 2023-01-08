import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "mysql+pymysql://root:1111Aa@127.0.0.1/usbstrela"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False