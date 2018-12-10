import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '39hrg9_a0v0i3jgifjncig!'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # to signal the application every time a change is about to be made in the database.

    #Email
    MAIL_SERVER = "192.168.220.32"
    MAIL_PORT = int(25)
    MAIL_USE_TLS = 0
    MAIL_USERNAME = "sendemail"
    MAIL_PASSWORD = "SEN123asd"
    ADMINS = ['chris.wong@xyzq.com.hk']


    #System


    #Admin