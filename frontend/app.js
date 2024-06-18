import React, { useState, useEffect } from 'react';
import axios from 'axios';
import JobApplicationForm from './components/JobApplicationForm';
import JobApplicationList from './components/JobApplicationList';

const App = () => {
  const [applications, setApplications] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/applications')
      .then(response => setApplications(response.data))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  const addApplication = (application) => {
    setApplications([...applications, application]);
  };

  return (
    <div>
      <h1>Job Tracker</h1>
      <JobApplicationForm addApplication={addApplication} />
      <JobApplicationList applications={applications} />
    </div>
  );
};

export default App;