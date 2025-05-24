import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

const DetailPage = () => {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:3000/data");
        const data = await res.json();
        if (id >= 0 && id < data.length) {
          setItem(data[id]);
        } else {
          setItem(null);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        setItem(null);
      }
    };

    fetchData();
  }, [id]);

  const renderField = (label, value) => (
    <div className="mb-4">
      <h3 className="text-lg font-semibold text-gray-700 mb-1 capitalize">{label}</h3>
      <p className="text-gray-800 bg-gray-50 rounded-lg px-4 py-2 border border-gray-200">{value || "—"}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-3xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="text-indigo-600 hover:underline mb-6 block"
        >
          ← Back To Previews
        </button>

        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">Trip Details</h1>

          {item ? (
            <div className="space-y-6">
              {Object.entries(item).map(([key, value]) => {
                const displayValue =
                  typeof value === "object"
                    ? JSON.stringify(value, null, 2)
                    : String(value);
                return renderField(key, displayValue);
              })}
            </div>
          ) : (
            <p className="italic text-red-500">No data found for this item.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default DetailPage;