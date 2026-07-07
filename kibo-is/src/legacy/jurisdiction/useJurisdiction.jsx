import React, { createContext, useContext, useState, useEffect } from 'react';

// Pre-load available packs for resolution
import caOnFippa from '../config/jurisdictions/ca-on-fippa.json';
import usCaCpra from '../config/jurisdictions/us-ca-cpra.json';
import caFederalPipeda from '../config/jurisdictions/ca-federal-pipeda.json';
import euGdpr from '../config/jurisdictions/eu-gdpr.json';

const packs = {
  'ca-on-fippa': caOnFippa,
  'us-ca-cpra': usCaCpra,
  'ca-federal-pipeda': caFederalPipeda,
  'eu-gdpr': euGdpr,
};

// Fallback pack if nothing resolves
const defaultPack = caOnFippa;

export const loadPack = (id) => {
  return packs[id] || defaultPack;
};

const JurisdictionContext = createContext({
  pack: defaultPack,
  t: (key, fallback) => fallback || key,
});

export const JurisdictionProvider = ({ packId, children }) => {
  const [pack, setPack] = useState(() => loadPack(packId));

  useEffect(() => {
    setPack(loadPack(packId));
  }, [packId]);

  const t = (key, fallback = '') => {
    return pack.terminology?.[key] || fallback || key;
  };

  return (
    <JurisdictionContext.Provider value={{ pack, t }}>
      {children}
    </JurisdictionContext.Provider>
  );
};

export const useJurisdiction = () => {
  return useContext(JurisdictionContext);
};
