import { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/register.css'; 

function Register({ onLoginSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password
        }),
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Registration failed');
      }

      onLoginSuccess(data.user);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <header className="register-header">
          <h2>Register</h2>
        </header>

        {error && <div className="register-error">{error}</div>}

        <form onSubmit={handleSubmit} className="register-form">
          <label htmlFor="name" className="register-label">Name</label>
          <input
            id="name"
            name="name"
            type="text"
            className="register-input"
            value={formData.name}
            onChange={handleChange}
            required
          />

          <label htmlFor="email" className="register-label">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            className="register-input"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <label htmlFor="password" className="register-label">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            className="register-input"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <label htmlFor="confirmPassword" className="register-label">Confirm Password</label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            className="register-input"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />

          <button className="register-button" disabled={isLoading}>
            {isLoading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <p className="register-login">
          Already have an account? <Link to="/login" className="register-login-link">Login</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;