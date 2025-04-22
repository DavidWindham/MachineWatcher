import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';

const EnergyGraph: React.FC<{ readings: any[] }> = ({ readings }) => {
  const data = readings.map(r => ({
    timestamp: r.timestamp * 1000,
    energy: r.aenergy.total,
  }));

  return (
    <>
      <h4>Total Energy (Wh)</h4>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            domain={['auto', 'auto']}
            tickFormatter={(ts) => new Date(ts).toLocaleTimeString()}
            type="number"
          />
          <YAxis unit=" Wh" />
          <Tooltip labelFormatter={(ts) => new Date(ts).toLocaleTimeString()} />
          <Line
            type="monotone"
            dataKey="energy"
            stroke="#82ca9d"
            strokeWidth={2}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </>
  );
};

export default EnergyGraph;
