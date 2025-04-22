import React from 'react';

export const LatestReadingTable: React.FC<{ reading: any }> = ({ reading }) => {
  const {
    apower,
    current,
    voltage,
    output,
    source,
    temperature,
    aenergy,
    timestamp
  } = reading;

  return (
    <div className="overflow-y-auto border rounded-xl p-4 shadow-md bg-white text-sm">
          <h4 className="text-lg font-semibold mb-2">Latest Reading</h4>
            <table className="table-auto w-full">
              <tbody>
                <tr><td className="font-medium">Power</td><td>{apower} W</td></tr>
                <tr><td className="font-medium">Current</td><td>{current} A</td></tr>
                <tr><td className="font-medium">Voltage</td><td>{voltage} V</td></tr>
                <tr><td className="font-medium">Temperature</td><td>{temperature.tC}°C / {temperature.tF}°F</td></tr>
                <tr><td className="font-medium">Output</td><td>{output ? 'On' : 'Off'}</td></tr>
                <tr><td className="font-medium">Energy (Total)</td><td>{aenergy.total.toFixed(2)} Wh</td></tr>
                <tr><td className="font-medium">Source</td><td>{source}</td></tr>
                <tr><td className="font-medium">Timestamp</td><td>{new Date(timestamp * 1000).toLocaleString()}</td></tr>
              </tbody>
            </table>
        </div>
  );
};

