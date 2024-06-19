from flask import Flask
from flask_cors import CORS
from backend.models import db, JobApplication
from backend.views import job_application_blueprint
import os
import datetime
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request





app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

db.init_app(app)
app.register_blueprint(job_application_blueprint)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobtracker.db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Use a secure key and store it safely
app.secret_key = 'your_flask_secret_key'  # Use a secure key for session management

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    google_credentials = db.Column(db.Text, nullable=True)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 400

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 400

    access_token = create_access_token(identity={'id': user.id})
    return jsonify({'token': access_token})

@app.route('/authorize')
@jwt_required()
def authorize():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
@jwt_required()
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    user.google_credentials = credentials.to_json()
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/add_event', methods=['POST'])
@jwt_required()
def add_event():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if not user.google_credentials:
        return jsonify({'message': 'Google Calendar not authorized'}), 400

    credentials = google.oauth2.credentials.Credentials(**user.google_credentials)
    service = build('calendar', 'v3', credentials=credentials)

    event_data = request.get_json()
    event = {
        'summary': event_data['summary'],
        'start': {'dateTime': event_data['start'], 'timeZone': 'UTC'},
        'end': {'dateTime': event_data['end'], 'timeZone': 'UTC'}
    }

    event = service.events().insert(calendarId='primary', body=event).execute()

    return jsonify({'message': 'Event created', 'event': event})

if __name__ == '__main__':
    app.run(debug=True)