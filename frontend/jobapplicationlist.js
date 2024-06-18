import React from 'react';

const JobApplicationList = ({ applications }) => {
  return (
    <div>
      <h2>Job Applications</h2>
      <ul>
        {applications.map(app => (
          <li key={app.id}>
            <strong>{app.job_title}</strong> at {app.company_name} on {app.application_date} - {app.status}
            <p>{app.notes}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default JobApplicationList;