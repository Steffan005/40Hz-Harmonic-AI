import { useEffect } from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
// PROGRESSIVE RESTORATION: FULL Unity with all backgrounds restored
// import { Unity } from "./pages/Unity_minimal";
import { Unity } from "./pages/Unity";
import { OfficeWindow } from "./pages/OfficeWindow";
import { api } from "./lib/api";
import "./App.css";

function App() {
  useEffect(() => {
    // Run initial preflight check
    const checkPreflight = async () => {
      try {
        await api.isPreflightPassed();
      } catch (err) {
        console.error("Preflight check failed:", err);
      }
    };

    checkPreflight();
  }, []);

  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Unity />} />
        <Route path="/office/:officeName" element={<OfficeWindow />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
