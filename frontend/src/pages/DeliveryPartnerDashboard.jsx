import { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import DashboardHeader from "../components/DashboardHeader";

export default function DeliveryPartnerDashboard() {
  const { userId } = useAuth();

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadOrders = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/orders/");
      setOrders(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to load orders."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const assignOrder = async (orderId) => {
    setError("");
    setMessage("");

    try {
      await api.patch(`/orders/${orderId}/assign-delivery`, {
        delivery_partner_id: Number(userId),
      });

      setMessage(`Order #${orderId} assigned successfully.`);
      await loadOrders();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to assign order."
      );
    }
  };

  const updateOrderStatus = async (orderId, status) => {
    setError("");
    setMessage("");

    try {
      await api.patch(`/orders/${orderId}/status`, { status });

      setMessage(`Order #${orderId} marked as ${status}.`);
      await loadOrders();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to update order."
      );
    }
  };

  const availableOrders = orders.filter(
    (order) =>
      order.status === "READY" && !order.delivery_partner_id
  );

  const myDeliveries = orders.filter(
    (order) =>
      Number(order.delivery_partner_id) === Number(userId)
  );

  if (loading) {
    return (
      <div className="page-container">
        <div className="dashboard-card">
          <p>Loading delivery dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <DashboardHeader title="Delivery Partner Dashboard" />
        <p>View available orders and manage your deliveries.</p>

        {error && <p className="error-message">{error}</p>}
        {message && <p>{message}</p>}

        <button type="button" onClick={loadOrders}>
          Refresh Dashboard
        </button>

        <hr />

        <h2>Available Orders</h2>

        {availableOrders.length === 0 && (
          <p>No orders are currently available for delivery.</p>
        )}

        <div className="restaurant-list">
          {availableOrders.map((order) => (
            <div className="restaurant-card" key={order.id}>
              <h3>Order #{order.id}</h3>
              <p>Restaurant ID: {order.restaurant_id}</p>
              <p>Customer ID: {order.customer_id}</p>
              <p>Amount: ₹{order.total_amount}</p>
              <p>Status: {order.status}</p>

              <button
                type="button"
                onClick={() => assignOrder(order.id)}
              >
                Accept Delivery
              </button>
            </div>
          ))}
        </div>

        <hr />

        <h2>My Deliveries</h2>

        {myDeliveries.length === 0 && (
          <p>You have not accepted any deliveries yet.</p>
        )}

        <div className="restaurant-list">
          {myDeliveries.map((order) => (
            <div className="restaurant-card" key={order.id}>
              <h3>Order #{order.id}</h3>
              <p>Restaurant ID: {order.restaurant_id}</p>
              <p>Customer ID: {order.customer_id}</p>
              <p>Amount: ₹{order.total_amount}</p>
              <p>Status: {order.status}</p>

              {order.status === "ASSIGNED" && (
                <button
                  type="button"
                  onClick={() =>
                    updateOrderStatus(order.id, "OUT_FOR_DELIVERY")
                  }
                >
                  Start Delivery
                </button>
              )}

              {order.status === "OUT_FOR_DELIVERY" && (
                <button
                  type="button"
                  onClick={() =>
                    updateOrderStatus(order.id, "DELIVERED")
                  }
                >
                  Mark as Delivered
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
