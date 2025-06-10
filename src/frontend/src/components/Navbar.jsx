import { Link } from 'react-router-dom';
import '../styles/Navbar.css'

function Navbar({ isAuthenticated, user, onLogout }) {
  const handleLogout = (e) => {
    e.preventDefault();
    onLogout();
  };

  return (
    <nav className='nav-section'>
      <div className='nav-bar'>
        <Link to="/" className="nav-logo">Text Summarizer</Link>
        
        <ul className='nav-links'>
          {isAuthenticated ? (
            <>
              <li className='nav-item'>
                <span className='nav-welcome'>Welcome, {user?.name || 'User'}</span>
              </li>
              <li className='nav-item'>
                <Link to="/" className="nav-link">Dashboard</Link>
              </li>
              <li className='nav-item'>
                <a href="#" className="nav-link" onClick={handleLogout}>Logout</a>
              </li>
            </>
          ) : (
            <>
              <li className='nav-item'>
                <Link to="/login" className="nav-link">Login</Link>
              </li>
              <li className='nav-item'>
                <Link to="/register" className="nav-link">Register</Link>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
