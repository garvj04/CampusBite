import { useEffect, useState } from "react";
import api from "../services/api";

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [allOrders, setAllOrders] = useState([]);
  const [orderStatusFilter, setOrderStatusFilter] = useState("");
  const [restaurantFilter, setRestaurantFilter] = useState("");
  const [orderPage, setOrderPage] = useState(1);
  const [hasMoreOrders, setHasMoreOrders] = useState(false);
  const [payments, setPayments] = useState([]);
  const [logs, setLogs] = useState([]);
  const [orderId, setOrderId] = useState("");
  const [message, setMessage] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadAllOrders = async () => {
    const collectedOrders = [];
    let page = 1;
    while (true) {
      const response = await api.get("/orders/", { params: { page, page_size: 100 } });
      collectedOrders.push(...response.data);
      if (response.data.length < 100) break;
      page += 1;
    }
    return collectedOrders;
  };

  const loadOrders = async () => {
    try {
      const response = await api.get("/orders/", {
        params: {
          status: orderStatusFilter || undefined,
          restaurant_id: restaurantFilter ? Number(restaurantFilter) : undefined,
          page: orderPage,
          page_size: 10,
        },
      });
      setOrders(response.data);
      setHasMoreOrders(response.data.length === 10);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load orders.");
    }
  };

  const loadDashboard = async () => {
    setLoading(true);
    setError("");

    try {
      const [u, o, p, l] = await Promise.all([
        api.get("/users/"),
        loadAllOrders(),
        api.get("/payments/"),
        api.get("/admin-reminder-logs/"),
      ]);

      setUsers(u.data);
      setAllOrders(o);
      setPayments(p.data);
      setLogs(l.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load dashboard.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  useEffect(() => {
    loadOrders();
  }, [orderPage, orderStatusFilter, restaurantFilter]);

  const createReminder = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    try {
      await api.post("/admin-reminder-logs/", {
        order_id: orderId ? Number(orderId) : null,
        message,
        status: "PENDING",
      });

      setOrderId("");
      setMessage("");
      setNotice("Reminder created successfully.");
      await loadDashboard();
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to create reminder.");
    }
  };

  if (loading) {
    return <div className="page-container"><div className="dashboard-card">Loading admin dashboard...</div></div>;
  }

  const delivered = allOrders.filter(o => o.status === "DELIVERED").length;
  const pending = allOrders.filter(o => !["DELIVERED", "CANCELLED", "REFUNDED"].includes(o.status)).length;
  const paidAmount = payments.filter(p => p.status === "PAID").reduce((sum, p) => sum + p.amount, 0);

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <h1>Admin Dashboard</h1>
        {error && <p className="error-message">{error}</p>}
        {notice && <p>{notice}</p>}
        <button onClick={loadDashboard}>Refresh Dashboard</button>

        <h2>Platform Overview</h2>
        <div className="restaurant-list">
          <div className="restaurant-card"><h3>Total Users</h3><p>{users.length}</p></div>
          <div className="restaurant-card"><h3>Total Orders</h3><p>{allOrders.length}</p></div>
          <div className="restaurant-card"><h3>Pending Orders</h3><p>{pending}</p></div>
          <div className="restaurant-card"><h3>Delivered Orders</h3><p>{delivered}</p></div>
          <div className="restaurant-card"><h3>Paid Amount</h3><p>₹{paidAmount.toFixed(2)}</p></div>
        </div>

        <hr />
        <h2>Users</h2>
        <div className="restaurant-list">
          {users.map(user => (
            <div className="restaurant-card" key={user.id}>
              <h3>{user.name}</h3>
              <p>{user.email}</p>
              <p>Role: {user.role}</p>
            </div>
          ))}
        </div>

        <hr />
        <h2>All Orders</h2>
        <label>Filter by Status</label>
        <select value={orderStatusFilter} onChange={event => { setOrderStatusFilter(event.target.value); setOrderPage(1); }}>
          <option value="">All Statuses</option>
          {["PLACED","ACCEPTED","PREPARING","READY","ASSIGNED","OUT_FOR_DELIVERY","DELIVERED","CANCELLED","REFUNDED"].map(status => <option key={status} value={status}>{status}</option>)}
        </select>
        <label>Filter by Restaurant ID</label>
        <input type="number" min="1" placeholder="Enter restaurant ID" value={restaurantFilter} onChange={event => { setRestaurantFilter(event.target.value); setOrderPage(1); }} />
        <div className="restaurant-list">
          {orders.length === 0 ? (
            <p>No orders found.</p>
          ) : orders.map(order => (
            <div className="restaurant-card" key={order.id}>
              <h3>Order #{order.id}</h3>
              <p>Customer ID: {order.customer_id}</p>
              <p>Restaurant ID: {order.restaurant_id}</p>
              <p>Amount: ₹{order.total_amount}</p>
              <p>Status: {order.status}</p>
              <p>Delivery Partner: {order.delivery_partner_id || "Not assigned"}</p>
            </div>
          ))}
        </div>

        <div className="pagination-controls">
          <button onClick={() => setOrderPage(page => Math.max(1, page - 1))} disabled={orderPage === 1}>Previous</button>
          <span>Page {orderPage}</span>
          <button onClick={() => setOrderPage(page => page + 1)} disabled={!hasMoreOrders}>Next</button>
        </div>

        <hr />
        <h2>Payment Ledger</h2>
        <div className="restaurant-list">
          {payments.map(payment => (
            <div className="restaurant-card" key={payment.id}>
              <h3>Payment #{payment.id}</h3>
              <p>Order ID: {payment.order_id}</p>
              <p>Amount: ₹{payment.amount}</p>
              <p>Status: {payment.status}</p>
              <p>Method: {payment.payment_method}</p>
              <p>Transaction: {payment.transaction_id}</p>
            </div>
          ))}
        </div>

        <hr />
        <h2>Create Reminder Log</h2>
        <form onSubmit={createReminder}>
          <label>Order ID (optional)</label>
          <input
            type="number"
            min="1"
            value={orderId}
            onChange={event => setOrderId(event.target.value)}
          />

          <label>Reminder Message</label>
          <textarea
            value={message}
            onChange={event => setMessage(event.target.value)}
            required
          />

          <button type="submit">Create Reminder</button>
        </form>

        <h2>Admin Reminder Logs</h2>
        <div className="restaurant-list">
          {logs.map(log => (
            <div className="restaurant-card" key={log.id}>
              <h3>Reminder #{log.id}</h3>
              <p>Order ID: {log.order_id || "General"}</p>
              <p>{log.message}</p>
              <p>Status: {log.status}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
