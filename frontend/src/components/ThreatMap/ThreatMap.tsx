// src/components/ThreatMap/ThreatMap.tsx
import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ThreatPoint {
  lat: number;
  lng: number;
  severity: string;
  description: string;
}

const ThreatMap = () => {
  const [threats, setThreats] = useState<ThreatPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchThreats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/metrics/geographic');
        const data = await response.json();
        setThreats(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch threat data');
        setLoading(false);
      }
    };

    fetchThreats();
    const interval = setInterval(fetchThreats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-2xl font-bold">Threat Map</h2>
      </CardHeader>
      <CardContent>
        <div className="h-96 w-full bg-gray-100 rounded-lg">
          {/* Placeholder for map implementation */}
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">Map visualization would go here</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ThreatMap;