import { useLocation, useNavigate } from "react-router-dom";

export default function OrderSuccess() {
  const location = useLocation();
  const navigate = useNavigate();

  const { orderId, total } = location.state || {};

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <h1>Order Placed Successfully!</h1>

        {orderId && (
          <p>
            Your order number is <strong>#{orderId}</strong>.
          </p>
        )}

        {typeof total === "number" && (
          <p>
            Total paid: <strong>₹{total.toFixed(2)}</strong>
          </p>
        )}

        <p>Your order has been placed and is waiting for restaurant confirmation.</p>

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
