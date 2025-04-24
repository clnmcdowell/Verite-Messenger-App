<script lang="ts">
    import PeerList from '../components/PeerList.svelte';
    import ChatWindow from '../components/ChatWindow.svelte';
    import MessageInput from '../components/MessageInput.svelte';
    import type { Peer, Message } from '../components/types';
    import { fetchPeers, registerPeer, sendHeartbeat } from '../lib/api';
    import { onMount, onDestroy } from 'svelte';
    import { listen } from '@tauri-apps/api/event';
    import { invoke } from '@tauri-apps/api/core';
    
    // TODO: replace with real config
    const PEER_ID = 'peer1';
    const LISTEN_PORT = 5001;

    // Reactive state
    let peers: Peer[] = [];
    let selectedPeer: Peer | null = null;
    let messages: Message[] = [];

    // Holds the active socket ID returned by `start_chat`
    let socketId: number | null = null;

    /** Fetch & reload the peer list from the discovery server */
    async function loadPeers() {
        try {
            peers = await fetchPeers();
        } catch (err) {
            console.error('[loadPeers]', err);
        }
    }

    /**
     * Called when user clicks a peer.
     * 1. Selects them
     * 2. Clears old messages
     * 3. Invokes `start_chat` to negotiate and open a socket
     */
    async function selectPeer(peer: Peer) {
        selectedPeer = peer;
        messages = [];

        try {
            socketId = await invoke<number>('start_chat', {
                peerIp: peer.ip,
                peerPort: peer.port,
                myId: PEER_ID,
            });
            console.log('[start_chat] got socketId', socketId);
        } catch (err) {
            console.error('[start_chat]', err);
        }
    }

    /** 
     * Called when user sends a message 
     * Appends it locally and then invokes the backend to send over TCP.
     * */
async function handleSend(content: string) {
        if (socketId === null) return;

        // Locally append it
        const outgoing: Message = {
            from: 'me',
            to: selectedPeer!.id,
            content,
            timestamp: new Date().toISOString()
        };
        messages = [...messages, outgoing];

        // Send it across the socket
        try {
            await invoke('send_message', { socketId, text: content });
        } catch (err) {
            console.error('[send_message]', err);
        }
    }

    /** Called when user clicks the attach file button */
    function handleSendFile() {
        // TODO: integrate real file picker and backend call
        alert("File send not implemented yet.")
    }

  onMount(async () => {
        // Tell Python to start listening on our port
        try {
            await invoke('init_listener', { port: LISTEN_PORT });
            console.log('[init_listener] listening on', LISTEN_PORT);
        } catch (err) {
            console.error('[init_listener]', err);
        }

        // Register & load peers
        try {
            await registerPeer(PEER_ID, LISTEN_PORT);
            console.log('[registerPeer] success');
        } catch (err) {
            console.error('[registerPeer]', err);
        }
        await loadPeers();

        // Heartbeat + refresh loop
        const interval = setInterval(async () => {
        try {
            await sendHeartbeat(PEER_ID);
            await loadPeers();
        } catch (err) {
            console.error('[heartbeat/loadPeers]', err);
        }
        }, 5000);

        // Listen for incoming chat‐messages from Python
        const unlisten = await listen<{ sid: number; text: string }>(
            'chat-message',
            event => {
                const { sid, text } = event.payload;
                // Only append if it's from the active chat
                if (sid === socketId) {
                    messages = [
                        ...messages,
                        {
                            from: selectedPeer!.id,
                            to: PEER_ID,
                            content: text,
                            timestamp: new Date().toISOString()
                        }
                    ];
                }
            }
        );

        // Cleanup on unmount
        onDestroy(() => {
            clearInterval(interval);
            unlisten(); // stop listening for chat-message events
        });
    });
</script>

<main class="app">
    <!-- Sidebar of peers -->
    <PeerList {peers} onSelect={selectPeer} />

    <!-- Chat + input section -->
    <div class="chat-section">
        <ChatWindow {messages} />
        <MessageInput onSend={handleSend} onSendFile={handleSendFile} />
    </div>
</main>

<style>
    .app {
        display: flex;
        height: 100vh;
        font-family: sans-serif;
    }
    .chat-section {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
</style>
