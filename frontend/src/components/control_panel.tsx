import React from 'react';

type Props = {
  onChange: () => void;
};

const ControlPanel: React.FC<Props> = ({ onChange }) => {
  const handleTurnOn = async () => {
    await fetch('/api/turn_machine_on', { method: 'POST' });
    onChange();
  };

  const handleTurnOff = async () => {
    await fetch('/api/turn_machine_off', { method: 'POST' });
    onChange();
  };

  return (
    <div className="fixed bottom-0 right-0 p-4 h-24 grid grid-cols-2 gap-4">
      <button onClick={handleTurnOn} className="rounded-xl bg-green-500 p-5">Turn Machine On</button>
      <button onClick={handleTurnOff} className="rounded-xl bg-red-500 p-5">Turn Machine Off</button>
    </div>
  );
};

export default ControlPanel;
