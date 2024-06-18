from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def authenticate_google_calendar():
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
    service = build('calendar', 'v3', credentials=creds)
    return service

def add_event_to_calendar(service, summary, description, start_time, end_time):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

# Fetch job listings (e.g., from Indeed)
job_listings = fetch_indeed_jobs('software engineer', 'San Francisco, CA')

# Authenticate Google Calendar
service = authenticate_google_calendar()

# Process each job listing
for job in job_listings:
    job_title = job['job_title']
    company_name = job['company_name']
    # Assume application deadline is one week from now
    start_time = datetime.datetime.now() + datetime.timedelta(days=7)
    end_time = start_time + datetime.timedelta(hours=1)
    
    add_event_to_calendar(
        service,
        summary=f"Apply to {job_title} at {company_name}",
        description=f"Application deadline for {job_title} at {company_name}.",
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat()
    )






if __name__ == '__main__':
    service = authenticate_google_calendar()
    add_event_to_calendar(service, 'Job Interview', 'Interview at XYZ Company', '2024-07-01T10:00:00-07:00', '2024-07-01T11:00:00-07:00')