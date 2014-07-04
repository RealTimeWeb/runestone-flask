from main import app

from frontend import frontend
app.register_blueprint(frontend)

from users import users
app.register_blueprint(users)

from assignments import assignments
app.register_blueprint(assignments)