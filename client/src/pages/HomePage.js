import React from 'react';
import { useNavigate } from 'react-router-dom';

function HomePage() {
  const navigate = useNavigate();

  const goToAboutPage = () => {
    navigate('/form');
  };

  // return (
  //   <div>
  //     <h1 class="text-4xl font-extrabold mb-4">Welcome to Your Travel Buddy!</h1>
  //     <button class="mt-6 px-6 py-3 bg-blue-600 text-white font-semibold rounded-full shadow-md hover:bg-blue-700 transition duration-300 ease-in-out"
  //             onClick={goToAboutPage}>Plan Your Dream Vacation!</button>
  //   </div>
  // );

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 font-inter text-gray-800">
      <div className="text-center p-8 bg-white rounded-xl shadow-2xl max-w-lg mx-auto">
        <h1 className="text-5xl font-extrabold mb-6 text-blue-700">
          Welcome to Your Travel Buddy!
        </h1>
        <p className="text-xl leading-relaxed mb-8">
          Plan Your Dream Vacation!
        </p>
        <button
          className="
            mt-6 px-8 py-4
            bg-gradient-to-r from-blue-500 to-indigo-600
            text-white font-bold text-lg
            rounded-full shadow-lg
            hover:from-blue-600 hover:to-indigo-700
            transform hover:scale-105
            transition duration-300 ease-in-out
            focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75
          "
          onClick={goToAboutPage}
        >
          take survey &rarr;
        </button>
      </div>
    </div>
  );
}

export default HomePage;