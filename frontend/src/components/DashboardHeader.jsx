import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function DashboardHeader({ title }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="dashboard-header">
      <h1>{title}</h1>
      <button type="button" onClick={handleLogout}>
        Log Out
      </button>
    </div>
  );
}
