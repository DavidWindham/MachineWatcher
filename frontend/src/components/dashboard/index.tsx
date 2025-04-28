import React from 'react';
import CurrentGraph from './current_graph';
import { LatestReadingTable } from './latest_reading_table';
import { CommandHistory, MachineStatus, Reading } from '../../App';

type Props = {
  readings: Reading[];
  status: MachineStatus | null;
  commandHistory?: CommandHistory[]; // New prop for command history
};

const Dashboard: React.FC<Props> = ({ readings, status, commandHistory = [] }) => {
  const latest = readings.length > 0 ? readings[readings.length - 1] : null;

  function formatTime(seconds: number | undefined) {
    if (!seconds && seconds !== 0) return '--:--:--';
    const totalSeconds = Math.floor(seconds);
    const hrs = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
    const mins = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
    const secs = String(totalSeconds % 60).padStart(2, '0');
    return `${hrs}:${mins}:${secs}`;
  }

  function formatDateTime(timestamp: number | undefined) {
    if (!timestamp) return '--';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  }

  return (
    <div className="flex flex-col gap-4 h-[calc(100vh-160px)]">
      {/* Top bar with status and latest reading */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-md">
          <h4 className="text-md font-semibold mb-2">Status</h4>
          <p><strong>Status:</strong> {status?.machine_on ? '🟢 ON' : '🔴 OFF'}</p>
          <p><strong>Uptime:</strong> {formatTime(status?.time_since_turned_on)}</p>
          <p><strong>Last turned on:</strong> {formatDateTime(status?.last_turned_on_at)}</p>
          {/* Command History Section */}
          <div className="bg-white rounded-xl p-4 shadow-md">
            <h4 className="text-md font-semibold mb-2">Command History</h4>
            <div className="max-h-32 overflow-y-auto">
              {commandHistory.length > 0 ? (
                <ul className="text-sm">
                  {commandHistory.slice().reverse().slice(0, 10).map((cmd, index) => (
                    <li key={index} className="py-1 border-b border-gray-100 last:border-0">
                      Machine was turned <span className={cmd.command_type === "on" ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
                        {cmd.command_type}
                      </span> at {cmd.formatted_time || formatDateTime(cmd.timestamp)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No command history available</p>
              )}
            </div>
          </div>
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