import { useEffect, useState } from 'react';
import ControlPanel from './components/control_panel';
import Dashboard from './components/dashboard';

type Reading = {
  aenergy: {
    by_minute: number[];
    minute_ts: number;
    total: number;
  };
  apower: number;
  current: number;
  id: number;
  output: boolean;
  source: string;
  temperature: {
    tC: number;
    tF: number;
  };
  timestamp: number;
  voltage: number;
};

type MachineStatus = {
  machine_on: boolean;
  machine_turned_on_at: number;
  time_since_turned_on: number;
};

function App() {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [status, setStatus] = useState<MachineStatus | null>(null);

  const fetchStatus = async () => {
    const res = await fetch('/api/get_machine_status');
    const data = await res.json();
    setReadings(data.readings);
    setStatus(data.status);
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 font-sans bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Machine Dashboard</h1>
      <Dashboard readings={readings} status={status} />
      <ControlPanel onChange={fetchStatus} />
    </div>
  );
}

export default App;
