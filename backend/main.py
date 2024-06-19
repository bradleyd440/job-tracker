import os.path
import base64
import re
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from bs4 import BeautifulSoup

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']






def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def list_messages(service, user_id='me', label_ids=['INBOX']):
    try:
        results = service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def get_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = MIMEText(msg_str)
        return mime_msg
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None
    
    
def fetch_linkedin_jobs():
    url = 'https://www.linkedin.com/jobs/search/?keywords=software%20engineer'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []
    for job in soup.find_all('div', class_='result-card__contents'):
        job_title = job.find('h3', class_='result-card__title').text.strip()
        company_name = job.find('h4', class_='result-card__subtitle').text.strip()
        jobs.append({'job_title': job_title, 'company_name': company_name})
    return jobs

def get_statistics():
    total_applications = JobApplication.query.filter_by(user_id=current_user.id).count()
    status_counts = db.session.query(JobApplication.status, db.func.count(JobApplication.status)).filter_by(user_id=current_user.id).group_by(JobApplication.status).all()
    return jsonify({
        'total_applications': total_applications,
        'status_counts': dict(status_counts)
    })
    
mail = Mail(app)

@app.route('/send_reminder_email/<int:id>', methods=['GET'])
def send_reminder_email(id):
    application = JobApplication.query.get_or_404(id)
    if application.reminder_date and application.reminder_date <= datetime.today().date():
        msg = Message('Reminder: Follow Up on Job Application',
                        recipients=[current_user.email])
        msg.body = f"Reminder to follow up on your application for {application.job_title} at {application.company_name}."
        mail.send(msg)
        return jsonify({"message": "Reminder email sent successfully!"}), 200
    return jsonify({"message": "No reminder needed today."}), 200   

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///job_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@example.com'
    MAIL_PASSWORD = 'your_password'
    MAIL_DEFAULT_SENDER = 'your_email@example.com'
    
@job_application_blueprint.route('/applications/<int:id>/set_reminder', methods=['POST'])
@login_required
def set_reminder(id):
    data = request.get_json()
    application = JobApplication.query.get_or_404(id)
    if application.user_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403
    reminder_date = datetime.strptime(data['reminder_date'], '%Y-%m-%d').date()
    application.reminder_date = reminder_date
    db.session.commit()
    return jsonify({"message": "Reminder set successfully!"}), 200

db = SQLAlchemy()

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reminder_date = db.Column(db.Date, nullable=True)
    
    
def parse_email_for_job_info(email_body):
    job_info = {}
    job_info['status'] = 'interview' if re.search(r'\binterview\b', email_body, re.IGNORECASE) else 'applied'
    job_info['follow_up_date'] = None
    match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', email_body)
    if match:
        job_info['follow_up_date'] = match.group(1)
    return job_info

def get_applications():
    status = request.args.get('status')
    sort_by = request.args.get('sort_by', 'application_date')
    order = request.args.get('order', 'asc')

    query = JobApplication.query.filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    
    if order == 'asc':
        query = query.order_by(getattr(JobApplication, sort_by).asc())
    else:
        query = query.order_by(getattr(JobApplication, sort_by).desc())

    applications = query.all()
    return jsonify([{
        'id': app.id,
        'job_title': app.job_title,
        'company_name': app.company_name,
        'application_date': app.application_date.strftime('%Y-%m-%d'),
        'status': app.status,
        'notes': app.notes
    } for app in applications])
    
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials!"}), 401
    login_user(user)
    return jsonify({"message": "User logged in successfully!"}), 200

@auth_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "User logged out successfully!"}), 200

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.register_blueprint(job_application_blueprint)
app.register_blueprint(auth_blueprint)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    
    #run.die = true-219