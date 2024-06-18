from flask import Blueprint, request, jsonify
from backend.models import db, JobApplication
from datetime import datetime

job_application_blueprint = Blueprint('job_application', __name__)

@job_application_blueprint.route('/applications', methods=['POST'])
def add_application():
    data = request.get_json()
    new_application = JobApplication(
        job_title=data['job_title'],
        company_name=data['company_name'],
        application_date=datetime.strptime(data['application_date'], '%Y-%m-%d').date(),
        status=data['status'],
        notes=data.get('notes', '')
    )
    db.session.add(new_application)
    db.session.commit()
    return jsonify({"message": "Job application added successfully!"}), 201

@job_application_blueprint.route('/applications', methods=['GET'])
def get_applications():
    applications = JobApplication.query.all()
    return jsonify([{
        'id': app.id,
        'job_title': app.job_title,
        'company_name': app.company_name,
        'application_date': app.application_date.strftime('%Y-%m-%d'),
        'status': app.status,
        'notes': app.notes
    } for app in applications])