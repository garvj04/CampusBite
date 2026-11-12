import { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import DashboardHeader from "../components/DashboardHeader";

const NEXT_STATUSES = {
  PLACED: ["ACCEPTED", "CANCELLED"],
  ACCEPTED: ["PREPARING", "CANCELLED"],
  PREPARING: ["READY", "CANCELLED"],
};

export default function RestaurantOwnerDashboard() {
  const { userId } = useAuth();

  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [orders, setOrders] = useState([]);
  const [orderStatusFilter, setOrderStatusFilter] = useState("");
  const [orderPage, setOrderPage] = useState(1);
  const [hasMoreOrders, setHasMoreOrders] = useState(false);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [ordersRefreshKey, setOrdersRefreshKey] = useState(0);
  const [statistics, setStatistics] = useState(null);
  const [deliveryPartners, setDeliveryPartners] = useState([]);
  const [selectedPartners, setSelectedPartners] = useState({});

  const [newRestaurantName, setNewRestaurantName] = useState("");
  const [newRestaurantDescription, setNewRestaurantDescription] = useState("");
  const [newRestaurantAddress, setNewRestaurantAddress] = useState("");

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadDashboard = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/restaurants/");

      const owned = response.data.find(
        (item) => Number(item.owner_id) === Number(userId)
      );

      if (!owned) {
        setRestaurant(null);
        setMenuItems([]);
        setOrders([]);
        setStatistics(null);
        setDeliveryPartners([]);
        return;
      }

      setRestaurant(owned);

      const [menu, stats, partners] = await Promise.all([
        api.get(`/menu-items/restaurant/${owned.id}`),
        api.get(`/restaurants/${owned.id}/statistics`),
        api.get("/users/delivery-partners"),
      ]);

      setMenuItems(menu.data);
      setStatistics(stats.data);
      setDeliveryPartners(partners.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to load dashboard."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) loadDashboard();
  }, [userId]);

  const loadOrders = async () => {
    if (!restaurant?.id) return;

    setOrdersLoading(true);
    try {
      const response = await api.get("/orders/", {
        params: {
          restaurant_id: restaurant.id,
          status: orderStatusFilter || undefined,
          page: orderPage,
          page_size: 10,
        },
      });

      setOrders(response.data);
      setHasMoreOrders(response.data.length === 10);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load orders.");
    } finally {
      setOrdersLoading(false);
    }
  };

  useEffect(() => {
    if (restaurant?.id) loadOrders();
  }, [restaurant?.id, orderPage, orderStatusFilter, ordersRefreshKey]);


  const createRestaurant = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      await api.post("/restaurants/", {
        name: newRestaurantName,
        description: newRestaurantDescription,
        address: newRestaurantAddress,
      });

      setNewRestaurantName("");
      setNewRestaurantDescription("");
      setNewRestaurantAddress("");
      setMessage("Restaurant created successfully.");
      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to create restaurant."
      );
    }
  };

  const assignDeliveryPartner = async (orderId) => {
    const partnerId = selectedPartners[orderId];

    if (!partnerId) {
      setError("Please select a delivery partner.");
      return;
    }

    setError("");
    setMessage("");

    try {
      await api.patch(`/orders/${orderId}/assign-delivery`, {
        delivery_partner_id: Number(partnerId),
      });

      setMessage(`Delivery partner assigned to Order #${orderId}.`);
      setSelectedPartners((current) => ({
        ...current,
        [orderId]: "",
      }));
      setOrdersRefreshKey((key) => key + 1);
      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to assign delivery partner."
      );
    }
  };

  const addMenuItem = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      await api.post("/menu-items/", {
        name,
        description,
        price: Number(price),
        restaurant_id: restaurant.id,
      });

      setName("");
      setDescription("");
      setPrice("");
      setMessage("Menu item added successfully.");
      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to add menu item."
      );
    }
  };

  const updateOrder = async (orderId, status) => {
    setError("");
    setMessage("");

    try {
      await api.patch(`/orders/${orderId}/status`, { status });
      setMessage(`Order #${orderId} updated successfully.`);
      setOrdersRefreshKey((key) => key + 1);
      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to update order."
      );
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="dashboard-card">
          <p>Loading restaurant dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="dashboard-card">
        <DashboardHeader title="Restaurant Owner Dashboard" />

        {error && (
          <p className="error-message">{error}</p>
        )}

        {message && <p>{message}</p>}

        {!restaurant && (
          <>
            <h2>Create Your Restaurant</h2>
            <p>No restaurant is linked to this owner account. Enter your restaurant details below to get started.</p>

            <form onSubmit={createRestaurant}>
              <label>Restaurant Name</label>
              <input
                value={newRestaurantName}
                onChange={(event) => setNewRestaurantName(event.target.value)}
                required
              />

              <label>Description</label>
              <input
                value={newRestaurantDescription}
                onChange={(event) => setNewRestaurantDescription(event.target.value)}
                required
              />

              <label>Address</label>
              <input
                value={newRestaurantAddress}
                onChange={(event) => setNewRestaurantAddress(event.target.value)}
                required
              />

              <button type="submit">Create Restaurant</button>
            </form>
          </>
        )}

        {restaurant && (
          <>
            <h2>{restaurant.name}</h2>
            <p>{restaurant.description}</p>
            <p>{restaurant.address}</p>

            <button onClick={loadDashboard}>
              Refresh Dashboard
            </button>

            <hr />

            <h2>Restaurant Statistics</h2>

            {statistics && (
              <div className="restaurant-list">
                <div className="restaurant-card">
                  <h3>Total Orders</h3>
                  <p>{statistics.total_orders}</p>
                </div>

                <div className="restaurant-card">
                  <h3>Delivered</h3>
                  <p>{statistics.delivered_orders}</p>
                </div>

                <div className="restaurant-card">
                  <h3>Cancelled</h3>
                  <p>{statistics.cancelled_orders}</p>
                </div>

                <div className="restaurant-card">
                  <h3>Revenue</h3>
                  <p>₹{statistics.total_revenue}</p>
                </div>

                <div className="restaurant-card">
                  <h3>Average Rating</h3>
                  <p>{statistics.average_rating}</p>
                </div>
              </div>
            )}

            <hr />

            <h2>Add Menu Item</h2>

            <form onSubmit={addMenuItem}>
              <label>Item Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />

              <label>Description</label>
              <input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />

              <label>Price (₹)</label>
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
              />

              <button type="submit">Add Menu Item</button>
            </form>

            <h2>Current Menu</h2>

            <div className="restaurant-list">
              {menuItems.map((item) => (
                <div className="restaurant-card" key={item.id}>
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                  <p>₹{item.price}</p>
                </div>
              ))}
            </div>

            <hr />

            <h2>Manage Orders</h2>

            <label>Filter by Status</label>
            <select
              value={orderStatusFilter}
              onChange={(event) => {
                setOrderStatusFilter(event.target.value);
                setOrderPage(1);
              }}
            >
              <option value="">All Statuses</option>
              {["PLACED","ACCEPTED","PREPARING","READY","ASSIGNED","OUT_FOR_DELIVERY","DELIVERED","CANCELLED","REFUNDED"].map((status) => (
                <option key={status} value={status}>{status.replaceAll("_", " ")}</option>
              ))}
            </select>

            {ordersLoading && <p>Loading orders...</p>}


            {orders.length === 0 && <p>No orders available.</p>}

            <div className="restaurant-list">
              {orders.map((order) => (
                <div className="restaurant-card" key={order.id}>
                  <h3>Order #{order.id}</h3>
                  <p>Customer ID: {order.customer_id}</p>
                  <p>Amount: ₹{order.total_amount}</p>
                  <p>Status: {order.status}</p>

                  {order.status === "READY" && !order.delivery_partner_id && (
                    <div>
                      <label>Assign Delivery Partner</label>
                      <select
                        value={selectedPartners[order.id] || ""}
                        onChange={(event) =>
                          setSelectedPartners((current) => ({
                            ...current,
                            [order.id]: event.target.value,
                          }))
                        }
                      >
                        <option value="">Select a delivery partner</option>
                        {deliveryPartners.map((partner) => (
                          <option key={partner.id} value={partner.id}>
                            {partner.name} (ID: {partner.id})
                          </option>
                        ))}
                      </select>

                      {deliveryPartners.length === 0 && (
                        <p>No delivery partners are available.</p>
                      )}

                      <button
                        type="button"
                        disabled={!selectedPartners[order.id]}
                        onClick={() => assignDeliveryPartner(order.id)}
                      >
                        Assign Delivery Partner
                      </button>
                    </div>
                  )}

                  {(NEXT_STATUSES[order.status] || []).map(
                    (status) => (
                      <button
                        key={status}
                        type="button"
                        onClick={() => updateOrder(order.id, status)}
                      >
                        {status.replaceAll("_", " ")}
                      </button>
                    )
                  )}
                </div>
              ))}
            </div>

            <div className="pagination-controls">
              <button
                type="button"
                onClick={() => setOrderPage((page) => Math.max(1, page - 1))}
                disabled={orderPage === 1 || ordersLoading}
              >
                Previous
              </button>

              <span>Page {orderPage}</span>

              <button
                type="button"
                onClick={() => setOrderPage((page) => page + 1)}
                disabled={!hasMoreOrders || ordersLoading}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}