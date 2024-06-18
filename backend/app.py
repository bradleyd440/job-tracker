from flask import Flask
from flask_cors import CORS
from backend.models import db, JobApplication
from backend.views import job_application_blueprint

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

db.init_app(app)
app.register_blueprint(job_application_blueprint)

if __name__ == '__main__':
    app.run(debug=True)