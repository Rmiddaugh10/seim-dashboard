import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Select } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { AlertCircle, CheckCircle, Search } from 'lucide-react';

const AlertList = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    severity: 'all',
    status: 'all',
    search: ''
  });

  useEffect(() => {
    fetchAlerts();
  }, [filters]);

  const fetchAlerts = async () => {
    try {
      let url = 'http://localhost:8000/api/v1/alerts?';
      if (filters.severity !== 'all') url += `severity=${filters.severity}&`;
      if (filters.status !== 'all') url += `status=${filters.status}&`;
      if (filters.search) url += `search=${encodeURIComponent(filters.search)}`;

      const response = await fetch(url);
      const data = await response.json();
      setAlerts(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch alerts');
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      await fetch(`http://localhost:8000/api/v1/alerts/${alertId}/acknowledge`, {
        method: 'POST'
      });
      fetchAlerts();
    } catch (err) {
      setError('Failed to acknowledge alert');
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

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
      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex space-x-4">
            <Select
              value={filters.severity}
              onChange={(e) => setFilters({...filters, severity: e.target.value})}
              className="w-48"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </Select>
            
            <Select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-48"
            >
              <option value="all">All Status</option>
              <option value="new">New</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </Select>

            <div className="flex-1 relative">
              <Input
                type="text"
                placeholder="Search alerts..."
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
                className="pl-10"
              />
              <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts.map((alert) => (
          <Card key={alert.id}>
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="h-5 w-5" />
                    <AlertTitle className="text-lg font-semibold">
                      {alert.title}
                    </AlertTitle>
                    <span className={`px-2 py-1 rounded text-sm ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <AlertDescription className="text-gray-600">
                    {alert.description}
                  </AlertDescription>
                  <div className="text-sm text-gray-500">
                    {new Date(alert.timestamp).toLocaleString()}
                  </div>
                </div>
                
                {alert.status === 'new' && (
                  <Button
                    variant="outline"
                    onClick={() => acknowledgeAlert(alert.id)}
                    className="flex items-center space-x-1"
                  >
                    <CheckCircle className="h-4 w-4" />
                    <span>Acknowledge</span>
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AlertList;