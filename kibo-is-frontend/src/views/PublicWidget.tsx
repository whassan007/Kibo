
import React, { useState } from "react";
export const PublicWidget = () => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  
  return (
    <div className="p-8 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">Submit Request</h1>
      {isOffline && <div className="bg-red-500 text-white p-2 mb-4">System is currently offline. Submissions paused.</div>}
      <button disabled={isOffline} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">Submit</button>
    </div>
  );
};
