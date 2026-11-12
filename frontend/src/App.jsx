import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login";
import CustomerDashboard from "./pages/CustomerDashboard";
import RestaurantMenu from "./pages/RestaurantMenu";
import CustomerOrder from "./pages/CustomerOrder";
import OrderSuccess from "./pages/OrderSuccess";
import RestaurantOwnerDashboard from "./pages/RestaurantOwnerDashboard";
import DeliveryPartnerDashboard from "./pages/DeliveryPartnerDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import CustomerOrders from "./pages/CustomerOrders";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";

function HomeRedirect() {
  const { isAuthenticated, role } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role === "CUSTOMER") {
    return <Navigate to="/customer" replace />;
  }

  if (role === "RESTAURANT_OWNER") {
    return <Navigate to="/restaurant" replace />;
  }

  if (role === "DELIVERY_PARTNER") {
    return <Navigate to="/delivery" replace />;
  }

  if (role === "ADMIN") {
    return <Navigate to="/admin" replace />;
  }

  return <Navigate to="/login" replace />;
}

function DashboardPlaceholder({ title }) {
  return (
    <div className="page-container">
      <div className="auth-card">
        <h1>{title}</h1>
        <p>CampusBite dashboard is being built.</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={<HomeRedirect />}
      />

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        element={
          <ProtectedRoute
            allowedRoles={["CUSTOMER"]}
          />
        }
      >
        <Route
          path="/customer"
          element={<CustomerDashboard />}
        />

        <Route
          path="/customer/restaurant/:restaurantId"
          element={<RestaurantMenu />}
        />

        <Route
          path="/customer/order"
          element={<CustomerOrder />}
        />

        <Route
          path="/customer/order/success"
          element={<OrderSuccess />}
        />

        <Route
          path="/customer/orders"
          element={<CustomerOrders />}
        />
      </Route>

      <Route
        element={
          <ProtectedRoute
            allowedRoles={["RESTAURANT_OWNER"]}
          />
        }
      >
        <Route
          path="/restaurant"
          element={
            <RestaurantOwnerDashboard />
          }
        />
      </Route>

      <Route
        element={
          <ProtectedRoute
            allowedRoles={["DELIVERY_PARTNER"]}
          />
        }
      >
        <Route
          path="/delivery"
          element={<DeliveryPartnerDashboard />}
        />
      </Route>

      <Route
        element={
          <ProtectedRoute
            allowedRoles={["ADMIN"]}
          />
        }
      >
        <Route
          path="/admin"
          element={<AdminDashboard />}

        />
      </Route>
    </Routes>
  );
}
