
export class FetchError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

export const fetchInbox = async (sort = "sla", type = "", q = "") => {
  const res = await fetch(`${API_BASE}/inbox?sort=${sort}&type=${type}&q=${q}`);
  if (!res.ok) throw new FetchError(res.status, "Failed to fetch inbox");
  return res.json();
};

export const submitDecision = async (id: string, action: string, reasoning: string, reclassify_to?: string) => {
  const res = await fetch(`${API_BASE}/inbox/${id}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, reasoning, reclassify_to })
  });
  if (!res.ok) throw new FetchError(res.status, "Failed to submit decision");
  return res.json();
};
