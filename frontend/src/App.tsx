import { useState } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import GuestSearch from "./pages/GuestSearch";
import ListingDetail from "./pages/ListingDetail";
import Landlord from "./pages/Landlord";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => {
  const [mode, setMode] = useState<"guest" | "landlord">("guest");

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <div className="min-h-screen w-full">
            <Navbar mode={mode} onModeChange={setMode} />
            <Routes>
              <Route path="/" element={<GuestSearch />} />
              <Route path="/listing/:id" element={<ListingDetail />} />
              <Route path="/landlord" element={<Landlord />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
