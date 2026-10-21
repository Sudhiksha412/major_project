// Base URL pointing to your backend
const API_BASE_URL = "http://localhost:8000";

// 1. Get System Status
export const getSystemStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/system-status`);
    if (!response.ok) throw new Error("Failed to fetch system status");
    return await response.json();
  } catch (error) {
    console.error("Error in getSystemStatus:", error);
    throw error; // Kept 'throw' so your frontend UI knows an error occurred
  }
};

// 2. Get Latest Analysis
export const getLatestAnalysis = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/latest-analysis`);
    if (!response.ok) throw new Error("Failed to fetch analysis");
    return await response.json();
  } catch (error) {
    console.error("Error in getLatestAnalysis:", error);
    throw error;
  }
};

// 3. Get Anomalies
export const getAnomalies = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/anomalies`);
    if (!response.ok) throw new Error("Failed to fetch anomalies");
    return await response.json();
  } catch (error) {
    console.error("Error in getAnomalies:", error);
    throw error;
  }
};
