// Shared TypeScript types for peers and messages

/** Represents a remote peer in the network */
export interface Peer {
  id: string;
  ip: string;
  port: number;
}

/** Represents a single chat message */
export interface Message {
  from: string;
  to: string;
  content: string;
  timestamp: string;
  isFile?: boolean; // Optional flag: true if this message is a file transfer
}
