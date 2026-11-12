import { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function CustomerOrders() {
  const { userId } = useAuth();

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [insight, setInsight] = useState("");
  const [insightLoading, setInsightLoading] = useState(false);
  const [reviews, setReviews] = useState({});
  const [messages, setMessages] = useState({});
  const [orderMessages, setOrderMessages] = useState({});

  const loadOrders = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/orders/");

      const myOrders = response.data.filter(
        (order) => Number(order.customer_id) === Number(userId)
      );

      const detailedOrders = await Promise.all(
        myOrders.map(async (order) => {
          const [itemsResult, paymentResult] = await Promise.allSettled([
            api.get(`/order-items/order/${order.id}`),
            api.get(`/payments/order/${order.id}`),
          ]);

          return {
            ...order,
            items: itemsResult.status === "fulfilled"
              ? itemsResult.value.data
              : [],
            payment: paymentResult.status === "fulfilled"
              ? paymentResult.value.data
              : null,
          };
        })
      );

      setOrders(detailedOrders);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to load your orders."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) loadOrders();
  }, [userId]);

  const loadInsight = async () => {
    setInsightLoading(true);
    setError("");

    try {
      const response = await api.get("/order-insight/");
      setInsight(response.data.insight);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to generate order insights."
      );
    } finally {
      setInsightLoading(false);
    }
  };

  const cancelOrder = async (order) => {
    try {
      await api.patch(`/orders/${order.id}/status`, {
        status: "CANCELLED",
      });
      await loadOrders();
      setOrderMessages((previous) => ({
        ...previous,
        [order.id]: "Order cancelled successfully.",
      }));
    } catch (err) {
      setOrderMessages((previous) => ({
        ...previous,
        [order.id]:
          err.response?.data?.detail || "Unable to cancel this order.",
      }));
    }
  };

  const submitReview = async (order) => {
    const review = reviews[order.id] || {
      rating: "5",
      comment: "",
    };

    try {
      await api.post("/reviews/", {
        customer_id: Number(userId),
        restaurant_id: order.restaurant_id,
        rating: Number(review.rating),
        comment: review.comment,
      });

      setMessages((previous) => ({
        ...previous,
        [order.id]: "Review submitted successfully.",
      }));
    } catch (err) {
      setMessages((previous) => ({
        ...previous,
        [order.id]:
          err.response?.data?.detail || "Unable to submit review.",
      }));
    }
  };

  const updateReview = (orderId, field, value) => {
    setReviews((previous) => ({
      ...previous,
      [orderId]: {
        rating: previous[orderId]?.rating || "5",
        comment: previous[orderId]?.comment || "",
        [field]: value,
      },
    }));
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="dashboard-card">
          <p>Loading your orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <h1>My Orders</h1>

        <button type="button" onClick={loadOrders}>
          Refresh Orders
        </button>

        <button
          type="button"
          onClick={loadInsight}
          disabled={insightLoading}
        >
          {insightLoading ? "Generating..." : "Get AI Order Insights"}
        </button>

        {error && <p className="error-message">{error}</p>}

        {insight && (
          <div className="restaurant-card">
            <h2>Your AI Order Insights</h2>
            <p>{insight}</p>
          </div>
        )}

        {orders.length === 0 && (
          <p>You have not placed any orders yet.</p>
        )}

        <div className="restaurant-list">
          {orders.map((order) => (
            <div className="restaurant-card" key={order.id}>
              <h2>Order #{order.id}</h2>
              <p>Restaurant ID: {order.restaurant_id}</p>
              <p>Total: ₹{order.total_amount}</p>
              <p>Status: <strong>{order.status}</strong></p>

              {order.status === "PLACED" && (
                <button type="button" onClick={() => cancelOrder(order)}>
                  Cancel Order
                </button>
              )}

              {orderMessages[order.id] && (
                <p role="status">{orderMessages[order.id]}</p>
              )}

              <h3>Items</h3>
              {order.items.length === 0 && <p>No item details available.</p>}

              {order.items.map((item) => (
                <p key={item.id}>
                  Menu Item #{item.menu_item_id} × {item.quantity}
                  {" — "}₹{item.price}
                </p>
              ))}

              <h3>Payment</h3>
              {order.payment ? (
                <>
                  <p>Status: {order.payment.status}</p>
                  <p>Method: {order.payment.payment_method}</p>
                  <p>Transaction: {order.payment.transaction_id}</p>
                </>
              ) : (
                <p>No payment record found.</p>
              )}

              {order.status === "DELIVERED" && (
                <>
                  <hr />
                  <h3>Review Restaurant</h3>

                  <label>Rating</label>
                  <select
                    value={reviews[order.id]?.rating || "5"}
                    onChange={(event) =>
                      updateReview(order.id, "rating", event.target.value)
                    }
                  >
                    {[5, 4, 3, 2, 1].map((rating) => (
                      <option key={rating} value={rating}>
                        {rating} / 5
                      </option>
                    ))}
                  </select>

                  <label>Comment</label>
                  <textarea
                    value={reviews[order.id]?.comment || ""}
                    onChange={(event) =>
                      updateReview(order.id, "comment", event.target.value)
                    }
                    placeholder="Write your review"
                  />

                  <button
                    type="button"
                    onClick={() => submitReview(order)}
                  >
                    Submit Review
                  </button>

                  {messages[order.id] && (
                    <p>{messages[order.id]}</p>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
