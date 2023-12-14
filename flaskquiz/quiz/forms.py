# -*- coding: utf-8 -*-
"""Quiz forms."""
from flask_wtf import FlaskForm
from flask import current_app
import requests
from wtforms import RadioField
from wtforms.validators import DataRequired

from flaskquiz.user.models import User


class QuizForm(FlaskForm):
    """Login form."""

    answer = RadioField("Answer", validators=[DataRequired()])
