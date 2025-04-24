import React from 'react';
import CurrentGraph from './current_graph';
import { LatestReadingTable } from './latest_reading_table';

type Props = {
  readings: any[];
  status: any;
};

const Dashboard: React.FC<Props> = ({ readings, status }) => {
  const latest = readings[readings.length - 1];

  function formatTime(seconds: number) {
    if (!seconds && seconds !== 0) return '--:--:--';

    const totalSeconds = Math.floor(seconds);
    const hrs = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
    const mins = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
    const secs = String(totalSeconds % 60).padStart(2, '0');

    return `${hrs}:${mins}:${secs}`;
  }

  return (
    <div className="flex flex-col gap-4 h-[calc(100vh-160px)]">
      {/* Top bar with status and latest reading */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-md">
          {status && (
            <div>
              <h4 className="text-md font-semibold mb-2">Status</h4>
              <p><strong>Status:</strong> {status.machine_on ? '🟢 ON' : '🔴 OFF'}</p>
              {/* <p><strong>Uptime:</strong> {status.time_since_turned_on?.toFixed(2)} seconds</p> */}
              <p><strong>Uptime:</strong> {formatTime(status.time_since_turned_on)}</p>
            </div>
          )}
        </div>

        {latest && <LatestReadingTable reading={latest} />}
      </div>

      {/* Graph full width */}
      <div className="flex-grow min-h-0 overflow-hidden">
        <CurrentGraph readings={readings} />
      </div>
    </div>
  );

};

export default Dashboard;
