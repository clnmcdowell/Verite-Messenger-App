import type { Peer } from "../components/types";

const BASE_URL = "http://localhost:8000";

/** Get a list of peers from the discovery server */
export async function fetchPeers(): Promise<Peer[]> {
  try {
    const res = await fetch(`${BASE_URL}/peers`);
    if (!res.ok) throw new Error(`Server responded with ${res.status}`);
    const peers = await res.json();
    return peers;
  } catch (err) {
    console.error("[fetchPeers] error:", err);
    return [];
  }
}
