import type { Peer } from "../components/types";

const BASE_URL = "http://localhost:8000"; // Discovery server address

/**
 * Fetch the list of currently active peers.
 * @returns Promise resolving to an array of Peer objects.
 */
export async function fetchPeers(): Promise<Peer[]> {
  try {
    const res = await fetch(`${BASE_URL}/peers`);
    if (!res.ok) {
      // Server returned an error status
      throw new Error(`Status ${res.status}`);
    }
    // Parse JSON array of peers
    return await res.json();
  } catch (err) {
    console.error("[fetchPeers] failed:", err);
    return []; // Return empty list on failure
  }
}

/**
 * Register this client with the discovery server.
 * Sends a POST /register { id, port } so others can discover you.
 * @param id    Unique peer identifier
 * @param port  TCP port this client will listen on
 */
export async function registerPeer(id: string, port: number): Promise<void> {
  try {
    const res = await fetch(`${BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, port }),
    });
    if (!res.ok) {
      throw new Error(`Register failed: ${res.status}`);
    }
    console.log(`[registerPeer] registered id=${id} port=${port}`);
  } catch (err) {
    console.error("[registerPeer] error:", err);
  }
}

/**
 * Send a heartbeat to keep this client marked as active.
 * GET /heartbeat?peer_id={id} updates your last_seen timestamp on the server.
 * @param id  Your peer ID
 */
export async function sendHeartbeat(id: string): Promise<void> {
  try {
    const res = await fetch(
      `${BASE_URL}/heartbeat?peer_id=${encodeURIComponent(id)}`,
      {
        method: "POST",
      }
    );
    if (!res.ok) {
      console.warn(`[sendHeartbeat] non-OK status ${res.status}`);
    }
  } catch (err) {
    console.error("[sendHeartbeat] error:", err);
  }
}
