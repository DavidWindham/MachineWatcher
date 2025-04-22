import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';

const CurrentGraph: React.FC<{ readings: any[] }> = ({ readings }) => {
  const data = readings.map(r => ({
    timestamp: r.timestamp * 1000,
    current: r.current,
  }));

  const maxCurrent = Math.max(...data.map(d => d.current));
  const paddedMax = maxCurrent * 1.05; // 10% overhead

  return (
    <>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            type="number"
            domain={['auto', 'auto']}
            tickFormatter={(ts) => new Date(ts).toLocaleTimeString()}
          />
          <YAxis
            unit=" A"
            domain={[0, paddedMax]}
            allowDataOverflow={false}
          />
          <Tooltip labelFormatter={(ts) => new Date(ts).toLocaleTimeString()} />
          <Line
            type="monotone"
            dataKey="current"
            stroke="#8884d8"
            strokeWidth={2}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </>
  );
};

export default CurrentGraph;
