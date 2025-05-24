import React from 'react';
import { useNavigate } from 'react-router-dom';

function HomePage() {
  const navigate = useNavigate();

  const goToAboutPage = () => {
    navigate('/form');
  };

  return (
    <div>
      <h1>Welcome to the Home Page!</h1>
      <p>This is the first page.</p>
      <button onClick={goToAboutPage}>Go to About Page</button>
    </div>
  );
}

export default HomePage;