from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length

class SendEmailForm(FlaskForm):

     def __init__(self):
         FlaskForm.__init__()
