# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user
import requests

from flaskquiz.extensions import login_manager
from flaskquiz.public.forms import LoginForm, WeatherForm
from flaskquiz.user.forms import RegisterForm
from flaskquiz.user.models import User
from flaskquiz.utils import flash_errors
from flaskquiz.settings import OWM_API_KEY

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    redirect_url = url_for("public.weather")
    return redirect(redirect_url)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", login_form=form)


@blueprint.route("/weather", methods=["GET", "POST"])
def weather():
    """Weather page."""
    form = LoginForm(request.form)
    weather_form = WeatherForm(request.form)

    if request.method == "POST":
        if weather_form.validate_on_submit():
            city = weather_form.city.data
            url = 'http://api.openweathermap.org/data/2.5/forecast?q={0}&appid={1}&units=metric&cnt=10'.format(
                city,
                OWM_API_KEY
            )
            r = requests.get(url)
            weathers = r.json()['list']
            for weather in weathers:
                timestamp = weather['dt']
                datetime_obj = datetime.datetime.utcfromtimestamp(timestamp)
                weather['dt'] = datetime_obj

            return render_template("public/weather-list.html", login_form=form, weathers=weathers)
        else:
            flash_errors(weather_form)
    return render_template("public/weather.html", login_form=form, weather_form=weather_form)


@blueprint.route("/scoreboard/")
def scoreboard():
    """Scoreboard page."""
    form = LoginForm(request.form)
    users = User.query.all()
    return render_template("public/scoreboard.html", login_form=form, users=users)
