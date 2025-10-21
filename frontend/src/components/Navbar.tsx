import { Home } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";

interface NavbarProps {
  mode: "guest" | "landlord";
  onModeChange: (mode: "guest" | "landlord") => void;
}

const Navbar = ({ mode, onModeChange }: NavbarProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const handleHomeClick = (e: React.MouseEvent) => {
    e.preventDefault();
    onModeChange("guest");
    navigate("/");
  };
  
  return (
    <nav className="sticky top-0 z-50 border-b bg-card shadow-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo/Brand */}
        <a href="/" onClick={handleHomeClick} className="flex items-center gap-2 text-xl font-semibold transition-colors hover:text-primary cursor-pointer">
          <Home className="h-6 w-6" />
          <span className="hidden sm:inline">AirBnBeautiful</span>
        </a>

        {/* Mode Toggle */}
        <div className="flex items-center gap-1 rounded-full bg-muted p-1">
          <button
            onClick={() => {
              onModeChange("guest");
              navigate("/");
            }}
            className={cn(
              "rounded-full px-4 py-2 text-sm font-medium transition-all",
              mode === "guest"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            Guest
          </button>
          <button
            onClick={() => {
              onModeChange("landlord");
              navigate("/landlord");
            }}
            className={cn(
              "rounded-full px-4 py-2 text-sm font-medium transition-all",
              mode === "landlord"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            Landlord
          </button>
        </div>

        {/* Avatar placeholder */}
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary text-sm font-medium">
          JD
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
