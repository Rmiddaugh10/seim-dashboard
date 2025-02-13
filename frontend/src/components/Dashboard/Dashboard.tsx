import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Shield, AlertTriangle, Activity } from 'lucide-react';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    securityScore: 0,
    alerts: [],
    threatTrend: [],
    eventDistribution: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/metrics/dashboard');
        const data = await response.json();
        setMetrics(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch dashboard data');
        setLoading(false);
      }
    };

    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Security Score Card */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="h-6 w-6" />
            <h2 className="text-2xl font-bold">Security Score</h2>
          </div>
          <span className="text-3xl font-bold">
            {Math.round(metrics.securityScore)}%
          </span>
        </CardHeader>
      </Card>

      {/* Threat Trend Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Activity className="h-6 w-6" />
            <h2 className="text-2xl font-bold">Threat Trend</h2>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-64 w-full">
            <ResponsiveContainer>
              <LineChart data={metrics.threatTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#0284c7" 
                  strokeWidth={2} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Recent Alerts */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-6 w-6" />
            <h2 className="text-2xl font-bold">Recent Alerts</h2>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {metrics.alerts.slice(0, 5).map((alert, index) => (
              <Alert key={index} variant={alert.severity === 'high' ? 'destructive' : 'default'}>
                <AlertDescription>
                  <div className="flex justify-between items-center">
                    <span>{alert.description}</span>
                    <span className="text-sm text-gray-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                </AlertDescription>
              </Alert>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;