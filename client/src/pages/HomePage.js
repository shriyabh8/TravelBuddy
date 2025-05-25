import React from 'react';
import { useNavigate } from 'react-router-dom';

import beachImage from '../assets/beach_img.jpeg';

function HomePage() {
  const navigate = useNavigate();

  const goToAboutPage = () => {
    navigate('/form');
  };

  return (
    <div className="flex items-center justify-center min-h-screen
    bg-cover bg-center bg-no-repeat relative overflow-hidden
    font-poppins text-gray-800"
          style={{ backgroundImage: `url(${beachImage})` }}>

      <div className="text-center p-12 bg-white rounded-xl shadow-2xl max-w-2xl mx-auto min-h-[40vh] flex flex-col justify-center items-center z-10">
        <h1 className="text-6xl font-poppins font-extrabold mb-8 text-cyan-700 leading-tight tracking-tight">
          Welcome to Travel Buddy!
        </h1>
        <p className="text-2xl italic font-open-sans leading-relaxed mb-12 mt-8 text-[#383a32] max-w-md">
          Travel Buddy will help you plan your dream vacation stress free!
        </p>
        <button
          className="
            mt-4 px-8 py-4
            bg-gradient-to-r from-[#36a2a4] to-cyan-700
            text-white font-open-sans font-bold text-lg
            rounded-2xl shadow-lg
            hover:from-[#36a2a4] hover:to-cyan-700
            transform hover:scale-105
            transition duration-300 ease-in-out
            focus:outline-none focus:ring-4 focus:ring-[#36a2a4] focus:ring-opacity-100
          "
          onClick={goToAboutPage}
        >
          Take Survey &rarr;
        </button>
      </div>
    </div>
  );
}

export default HomePage;