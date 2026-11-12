import { useLocation, useNavigate } from "react-router-dom";

export default function OrderSuccess() {
  const location = useLocation();
  const navigate = useNavigate();

  const {
    orderId,
    total,
    paymentStatus,
    transactionId,
  } = location.state || {};

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <h1>Order Placed Successfully!</h1>

        <p>Order Number: <strong>#{orderId}</strong></p>

        {typeof total === "number" && (
          <p>Total Amount: <strong>₹{total.toFixed(2)}</strong></p>
        )}

        <h2>Payment Details</h2>
        <p>Payment Status: <strong>{paymentStatus || "Not available"}</strong></p>
        {transactionId && <p>Transaction ID: {transactionId}</p>}

        <p>Your order is waiting for restaurant confirmation.</p>

        <button
          type="button"
          onClick={() => navigate("/customer/orders")}
        >
          View My Orders
        </button>

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
