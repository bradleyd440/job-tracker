import re

def parse_email_for_job_info(email_body):
    job_info = {}
    job_info['status'] = 'interview' if re.search(r'\binterview\b', email_body, re.IGNORECASE) else 'applied'
    job_info['follow_up_date'] = None
    match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', email_body)
    if match:
        job_info['follow_up_date'] = match.group(1)
    return job_info