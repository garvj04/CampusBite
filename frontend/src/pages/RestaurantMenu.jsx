import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function RestaurantMenu() {
  const { restaurantId } = useParams();
  const navigate = useNavigate();

  const [menuItems, setMenuItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchMenu = async () => {
      try {
        const response = await api.get(
          `/menu-items/restaurant/${restaurantId}`
        );
        setMenuItems(response.data);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            "Unable to load the restaurant menu."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchMenu();
  }, [restaurantId]);

  const addToCart = (item) => {
    setCart((currentCart) => {
      const existingItem = currentCart.find(
        (cartItem) => cartItem.id === item.id
      );

      if (existingItem) {
        return currentCart.map((cartItem) =>
          cartItem.id === item.id
            ? {
                ...cartItem,
                quantity: cartItem.quantity + 1,
              }
            : cartItem
        );
      }

      return [
        ...currentCart,
        {
          ...item,
          quantity: 1,
        },
      ];
    });
  };

  const removeFromCart = (itemId) => {
    setCart((currentCart) =>
      currentCart.filter((item) => item.id !== itemId)
    );
  };

  const cartTotal = cart.reduce(
    (total, item) => total + item.price * item.quantity,
    0
  );

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <button
          type="button"
          onClick={() => navigate("/customer")}
        >
          ← Back to Restaurants
        </button>

        <h1>Restaurant Menu</h1>

        {loading && <p>Loading menu...</p>}

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        {!loading && !error && menuItems.length === 0 && (
          <p>No menu items are available.</p>
        )}

        {!loading && !error && menuItems.length > 0 && (
          <div className="restaurant-list">
            {menuItems.map((item) => (
              <div key={item.id} className="restaurant-card">
                <h3>{item.name}</h3>

                <p>
                  {item.description || "No description available."}
                </p>

                <p>
                  <strong>Price:</strong> ₹{item.price}
                </p>

                <button
                  type="button"
                  onClick={() => addToCart(item)}
                >
                  Add to Cart
                </button>
              </div>
            ))}
          </div>
        )}

        {cart.length > 0 && (
          <div className="cart-section">
            <h2>Cart</h2>

            {cart.map((item) => (
              <div key={item.id}>
                <p>
                  <strong>{item.name}</strong>
                  {" — "}
                  ₹{item.price} × {item.quantity}
                </p>

                <button
                  type="button"
                  onClick={() => removeFromCart(item.id)}
                >
                  Remove
                </button>
              </div>
            ))}

            <h3>Total: ₹{cartTotal.toFixed(2)}</h3>

            <button
              type="button"
              onClick={() =>
                navigate("/customer/order", {
                  state: {
                    restaurantId,
                    cart,
                    total: cartTotal,
                  },
                })
              }
            >
              Proceed to Order
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
