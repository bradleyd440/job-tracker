document.addEventListener('DOMContentLoaded', function() {
    const jobForm = document.getElementById('job-form');
    const jobList = document.getElementById('job-list');
  
    jobForm.addEventListener('submit', function(event) {
      event.preventDefault();
      const jobTitle = document.getElementById('job-title').value;
      const company = document.getElementById('company').value;
      const jobUrl = document.getElementById('job-url').value;
      const jobNotes = document.getElementById('job-notes').value;
  
      const job = { jobTitle, company, jobUrl, jobNotes };
      
      chrome.storage.local.get({ jobs: [] }, function(result) {
        const jobs = result.jobs;
        jobs.push(job);
        chrome.storage.local.set({ jobs }, function() {
          displayJobs();
        });
      });
    });
  
    function displayJobs() {
      chrome.storage.local.get({ jobs: [] }, function(result) {
        const jobs = result.jobs;
        jobList.innerHTML = '';
        jobs.forEach((job, index) => {
          const li = document.createElement('li');
          li.textContent = `${job.jobTitle} at ${job.company}`;
          jobList.appendChild(li);
        });
      });
    }
  
    displayJobs();
  });

  // When the user scrolls down 50px from the top of the document, resize the header's font size
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
    document.getElementById("icon-bar").style.fontSize = "10px";
  } else {
    document.getElementById("icon-bar").style.fontSize = "30px";
  }
}