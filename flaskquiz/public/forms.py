# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import FlaskForm
from flask import current_app
import requests
from wtforms import PasswordField, StringField, SelectField
from wtforms.validators import DataRequired

from flaskquiz.user.models import User
from flaskquiz.settings import OWM_API_KEY


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, **kwargs):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append("Unknown username")
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Invalid password")
            return False

        if not self.user.active:
            self.username.errors.append("User not activated")
            return False
        return True


class WeatherForm(FlaskForm):
    """Weather form."""

    city = StringField("City", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(WeatherForm, self).__init__(*args, **kwargs)

    def validate(self, **kwargs):
        """Validate the form."""
        initial_validation = super(WeatherForm, self).validate()
        if not initial_validation:
            return False

        url = 'http://api.openweathermap.org/geo/1.0/direct?q={0}&limit=1&appid={1}'.format(
            self.city.data,
            OWM_API_KEY
        )
        current_app.logger.info(url)
        r = requests.get(url)
        current_app.logger.info(r.json())
        if not r.json():
            self.city.errors.append("Invalid city name or non-existent")
            return False

        return True
