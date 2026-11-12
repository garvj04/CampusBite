import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function CustomerDashboard() {
  const navigate = useNavigate();

  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        const response = await api.get("/restaurants/");
        setRestaurants(response.data);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            "Unable to load restaurants."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRestaurants();
  }, []);

  const openRestaurant = (restaurantId) => {
    navigate(`/customer/restaurant/${restaurantId}`);
  };

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <h1>Customer Dashboard</h1>

        <p>
          Browse restaurants and choose what you want to order.
        </p>

        <h2>Restaurants</h2>

        {loading && <p>Loading restaurants...</p>}

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        {!loading && !error && restaurants.length === 0 && (
          <p>No restaurants are available.</p>
        )}

        {!loading && !error && restaurants.length > 0 && (
          <div className="restaurant-list">
            {restaurants.map((restaurant) => (
              <button
                key={restaurant.id}
                type="button"
                className="restaurant-card"
                onClick={() => openRestaurant(restaurant.id)}
              >
                <h3>{restaurant.name}</h3>

                <p>
                  {restaurant.description ||
                    "No description available."}
                </p>

                <p>
                  <strong>Address:</strong>{" "}
                  {restaurant.address}
                </p>

                <span>View Menu →</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
