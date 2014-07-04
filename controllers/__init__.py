from main import app

from models.models import User
from flask import session, g

@app.before_request
def load_user():
    if "user_email" in session and session["user_email"]:
        user = User.query.filter_by(email=session["user_email"]).first()
    else:
        user = None
    g.user = user

from frontend import frontend
app.register_blueprint(frontend)

from users import users
app.register_blueprint(users)

from instructor import instructor
app.register_blueprint(instructor)

from ajax import ajax
app.register_blueprint(ajax)

from assignments import assignments
app.register_blueprint(assignments)

from flask import redirect, url_for

@app.route('/')
def index():
    return redirect(url_for('users.index'))