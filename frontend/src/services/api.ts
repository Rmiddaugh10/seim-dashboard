/ src/services/api.ts
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const api = {
  async getAlerts() {
    const response = await fetch(`${API_BASE_URL}/alerts`);
    return response.json();
  },

  async getLogs() {
    const response = await fetch(`${API_BASE_URL}/logs`);
    return response.json();
  },

  async getDashboardMetrics() {
    const response = await fetch(`${API_BASE_URL}/metrics/dashboard`);
    return response.json();
  },

  async acknowledgeAlert(alertId: string) {
    const response = await fetch(`${API_BASE_URL}/alerts/${alertId}/acknowledge`, {
      method: 'POST'
    });
    return response.json();
  }
};