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
    document.getElementById("Snack-me").style.fontSize = "30px";
  } else {
    document.getElementById("Snack-me").style.fontSize = "90px";
  }
}

// When the user scrolls the page, execute myFunction
window.onscroll = function() {myFunction()};

// Get the header
var header = document.getElementById("icon-bar");

// Get the offset position of the navbar
var sticky = header.offsetTop;

// Add the sticky class to the header when you reach its scroll position. Remove "sticky" when you leave the scroll position
function myFunction() {
  if (window.pageYOffset > sticky) {
    header.classList.add("sticky");
  } else {
    header.classList.remove("sticky");
  }
}