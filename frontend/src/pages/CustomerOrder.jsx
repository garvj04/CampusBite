import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function CustomerOrder() {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId } = useAuth();

  const { restaurantId, cart, total } = location.state || {};

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!cart || cart.length === 0) {
    return (
      <div className="page-container">
        <div className="dashboard-card">
          <h1>Order</h1>
          <p>Your cart is empty.</p>
          <button
            type="button"
            onClick={() => navigate("/customer")}
          >
            Back to Restaurants
          </button>
        </div>
      </div>
    );
  }

  const placeOrder = async () => {
    setError("");

    if (!userId) {
      setError("Your user session could not be identified. Please log in again.");
      return;
    }

    setLoading(true);

    try {
      const orderResponse = await api.post("/orders/", {
        customer_id: Number(userId),
        restaurant_id: Number(restaurantId),
        total_amount: total,
      });

      const orderId = orderResponse.data.id;

      for (const item of cart) {
        await api.post("/order-items/", {
          order_id: orderId,
          menu_item_id: item.id,
          quantity: item.quantity,
          price: item.price,
        });
      }

      navigate("/customer/order/success", {
        state: {
          orderId,
          total,
        },
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to place the order."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <button
          type="button"
          onClick={() => navigate(-1)}
        >
          ← Back to Menu
        </button>

        <h1>Confirm Your Order</h1>
        <h2>Order Items</h2>

        {cart.map((item) => (
          <div key={item.id}>
            <p>
              <strong>{item.name}</strong>
              {" — "}
              ₹{item.price} × {item.quantity}
            </p>
          </div>
        ))}

        <h2>Total: ₹{total.toFixed(2)}</h2>

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        <button
          type="button"
          onClick={placeOrder}
          disabled={loading}
        >
          {loading ? "Placing Order..." : "Place Order"}
        </button>
      </div>
    </div>
  );
}
