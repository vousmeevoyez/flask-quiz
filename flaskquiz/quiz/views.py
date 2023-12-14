# -*- coding: utf-8 -*-
"""Quiz views."""
import random

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
import requests

from flask_login import current_user, login_required
from flaskquiz.extensions import cache,db 
from flaskquiz.quiz.forms import QuizForm
from flaskquiz.utils import flash_errors
from flaskquiz.user.models import User

blueprint = Blueprint("quiz", __name__, url_prefix="/quizzes", static_folder="../static")

@blueprint.route("/", methods=['GET', 'POST'])
@login_required
def quizzes():
    """List quizzes."""
    form = QuizForm(request.form)

    if request.method == "POST":
        answers = cache.get('answers')
        form.answer.choices = tuple(answers)

        if form.validate_on_submit():
            answer = cache.get(form.answer.data)

            if answer:
                user = User.query.filter_by(username=current_user.username).first()
                user.score += 1
                db.session.commit()

            cache.delete('answers')
            cache.delete(form.answer.data)

            redirect_url = url_for("user.members")
            return redirect(redirect_url)

    else:
        url = 'https://opentdb.com/api.php?amount=1&category=18&type=multiple'
        r = requests.get(url)
        if r.status_code != 200:
            return render_template("500.html")

        quiz = r.json()['results'][0]

        answers = quiz['incorrect_answers']
        answers.append(quiz['correct_answer'])
        random.shuffle(answers)

        quiz['answers'] = answers

        cache.set('answers', answers)
        cache.set(quiz['correct_answer'], quiz['question'])

        form.answer.choices = tuple(answers)

        return render_template("quizzes/quiz.html", form=form, quiz=quiz)
