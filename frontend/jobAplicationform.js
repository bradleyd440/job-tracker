import React, { useState } from 'react';
import axios from 'axios';

const JobApplicationForm = ({ addApplication }) => {
  const [formData, setFormData] = useState({
    job_title: '',
    company_name: '',
    application_date: '',
    status: '',
    notes: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/applications', formData)
      .then(response => {
        addApplication(formData);
        setFormData({
          job_title: '',
          company_name: '',
          application_date: '',
          status: '',
          notes: ''
        });
      })
      .catch(error => console.error('Error submitting form:', error));
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="job_title"
        value={formData.job_title}
        onChange={handleChange}
        placeholder="Job Title"
        required
      />
      <input
        type="text"
        name="company_name"
        value={formData.company_name}
        onChange={handleChange}
        placeholder="Company Name"
        required
      />
      <input
        type="date"
        name="application_date"
        value={formData.application_date}
        onChange={handleChange}
        required
      />
      <input
        type="text"
        name="status"
        value={formData.status}
        onChange={handleChange}
        placeholder="Status"
        required
      />
      <textarea
        name="notes"
        value={formData.notes}
        onChange={handleChange}
        placeholder="Notes"
      />
      <button type="submit">Add Application</button>
    </form>
  );
};

export default JobApplicationForm;