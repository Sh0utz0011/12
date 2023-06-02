from flask_wtf import  FlaskForm
from wtforms import SubmitField, SelectField
from flask_wtf.recaptcha import RecaptchaField

class MyForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')

class ChoiceForm(FlaskForm):
    flip_direction = SelectField('Flip Direction', choices=[('lr', 'Left/Right'), ('ud', 'Up/Down')])