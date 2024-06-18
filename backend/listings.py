import requests
from bs4 import BeautifulSoup

def fetch_indeed_jobs(query, location):
    url = f'https://www.indeed.com/jobs?q={query}&l={location}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    for job_card in soup.find_all('div', class_='jobsearch-SerpJobCard'):
        job_title = job_card.find('h2', class_='title').text.strip()
        company_name = job_card.find('span', class_='company').text.strip()
        location = job_card.find('div', class_='recJobLoc')['data-rc-loc']
        summary = job_card.find('div', class_='summary').text.strip()
        
        jobs.append({
            'job_title': job_title,
            'company_name': company_name,
            'location': location,
            'summary': summary
        })
    
    return jobs

if __name__ == '__main__':
    job_listings = fetch_indeed_jobs('software engineer', 'San Francisco, CA')
    for job in job_listings:
        print(job)