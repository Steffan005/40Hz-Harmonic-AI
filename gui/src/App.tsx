import { useState, useEffect } from "react";
import { Dashboard } from "./pages/Dashboard";
import { api } from "./lib/api";
import "./App.css";

function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Run initial preflight check
    const checkPreflight = async () => {
      try {
        const passed = await api.isPreflightPassed();
        setIsReady(passed);
      } catch (err) {
        console.error("Preflight check failed:", err);
        setIsReady(false);
      }
    };

    checkPreflight();
  }, []);

  return <Dashboard />;
}

export default App;
