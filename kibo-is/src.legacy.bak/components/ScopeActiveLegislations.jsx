import React, { useState } from 'react';

/**
 * ScopeActiveLegislations
 * Renders a hierarchical accordion of jurisdictions with checkboxes.
 * Props:
 * - jurisdictionsList: array of {code, flag, name, primary_statute, access_request_abbr}
 * - activeLegislations: array of selected jurisdiction codes
 * - setActiveLegislations: setter for activeLegislations
 * - setActiveJurisdiction: setter for the currently active jurisdiction (single string)
 * - handleJurisdictionChange: callback to notify surrounding app of jurisdiction change
 */
const ScopeActiveLegislations = ({
  jurisdictionsList,
  activeLegislations,
  setActiveLegislations,
  setActiveJurisdiction,
  handleJurisdictionChange,
}) => {
  // Group jurisdictions by region (simple mapping based on code prefixes)
  const regionMap = {
    canada: 'Canada',
    quebec: 'Canada',
    ontario: 'Canada',
    phipa: 'Canada',
    cyfsa: 'Canada',
    us: 'United States',
    eu: 'European Union',
  };

  const regions = {};
  jurisdictionsList.forEach((j) => {
    const region = regionMap[j.code] || 'Other';
    if (!regions[region]) regions[region] = [];
    regions[region].push(j);
  });

  const [openRegions, setOpenRegions] = useState({});

  const toggleRegion = (region) => {
    setOpenRegions((prev) => ({ ...prev, [region]: !prev[region] }));
  };

  const onCheckboxChange = (j) => {
    const isChecked = activeLegislations.includes(j.code);
    let next;
    if (isChecked) {
      next = activeLegislations.filter((x) => x !== j.code);
    } else {
      next = [...activeLegislations, j.code];
    }
    if (next.length === 0) return; // keep at least one
    setActiveLegislations(next);
    setActiveJurisdiction(next[0]);
    handleJurisdictionChange(next[0]);
  };

  return (
    <div className="relative inline-block text-left">
      <div className="flex items-center space-x-2 relative group">
        {/* Button toggle */}
        <button
          className="bg-white border border-[#E5E7EB] text-xs text-[#111827] px-3 py-1.5 rounded-lg focus:outline-none transition-all cursor-pointer flex items-center space-x-2"
          aria-haspopup="true"
        >
          <span className="font-semibold text-gray-800">
            Active Regs ({activeLegislations.length})
          </span>
          <span className="text-[10px] text-gray-400">▼</span>
        </button>
        <div
          className="absolute right-0 mt-1 w-80 bg-white border border-[#E5E7EB] rounded-xl shadow-xl p-3 z-50 hidden group-hover:block hover:block"
          role="tree"
        >
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">
            Scope Active Legislations
          </div>
          {Object.entries(regions).map(([region, list]) => (
            <div key={region} className="mb-2">
              <button
                type="button"
                className="w-full text-left text-xs font-medium text-gray-600 flex items-center justify-between"
                onClick={() => toggleRegion(region)}
                aria-expanded={!!openRegions[region]}
              >
                {region}
                <span>{openRegions[region] ? '▲' : '▼'}</span>
              </button>
              {openRegions[region] && (
                <div className="mt-1 space-y-1" role="group">
                  {list.map((j) => {
                    const isChecked = activeLegislations.includes(j.code);
                    return (
                      <label
                        key={j.code}
                        className="flex items-center space-x-2.5 text-xs text-gray-700 cursor-pointer select-none"
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => onCheckboxChange(j)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="font-medium">
                          {j.flag} {j.name}
                        </span>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ScopeActiveLegislations;
