import React from 'react';
import mockData from '../data/mockShadowRisk.json';

const ShadowRiskFeed = () => {
  return (
    <div className="bg-white bg-opacity-30 backdrop-blur-lg rounded-xl border border-white/20 p-4 shadow-md">
      <h3 className="text-sm font-semibold text-gray-800 mb-2">Shadow Risk Feed</h3>
      {mockData.map((item) => (
        <div key={item.id} className="flex items-start space-x-2 mb-2">
          <div className={`w-2 h-2 rounded-full mt-1 flex-shrink-0 ${item.severity === 'high' ? 'bg-red-500' : item.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'}`} />
          <div className="text-xs text-gray-700">
            <span className="font-medium">{item.title}</span> – {item.description}
            <div className="text-xs text-gray-500">{new Date(item.timestamp).toLocaleString()}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ShadowRiskFeed;
