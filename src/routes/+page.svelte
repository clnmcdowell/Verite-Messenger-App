<script lang="ts">
    import PeerList from '../components/PeerList.svelte';
    import ChatWindow from '../components/ChatWindow.svelte';
    import MessageInput from '../components/MessageInput.svelte';
    import type { Peer, Message } from '../components/types';
    import { fetchPeers } from '../lib/api';
    import { registerPeer, sendHeartbeat } from '../lib/api';
    import { onMount } from 'svelte';
    import { onDestroy } from 'svelte';

    // TODO: replace with real config
    const PEER_ID = 'peer1';
    const LISTEN_PORT = 5001;

    // Currently selected peer (null = no selection)
    let selectedPeer: Peer | null = null

    let peers: Peer[] = [];

    // Chat history; new messages get appended here
    let messages: Message[] = []

    /** Called when user selects a peer from the sidebar */
    function selectPeer(peer: Peer) {
        selectedPeer = peer
        messages = []  // Clear chat history for new peer
    }

    /** Called when user sends a message */
    function handleSend(content: string) {
        if (!selectedPeer) return
        const msg: Message = {
        from: 'me',
        to: selectedPeer.id,
        content,
        timestamp: new Date().toISOString()
        }
        messages = [...messages, msg]  // Append to history
    }

    /** Called when user clicks the attach file button */
    function handleSendFile() {
        // TODO: integrate real file picker and backend call
        alert("File send not implemented yet.")
    }

    /** Function to load list of peers */
    async function loadPeers() {
        try {
            peers = await fetchPeers();
        } catch (err) {
            console.error('[loadPeers]', err);
        }
    }

    onMount(async () => {
        // Register this peer with the server
        try {
            await registerPeer(PEER_ID, LISTEN_PORT);
            console.log('[registerPeer] success');
        } catch (err) {
            console.error('[registerPeer]', err);
        }

        // Load the list of peers
        await loadPeers();

        // Start sending heartbeat to server every 5 seconds
        const interval = setInterval(async () => {
            try {
                await sendHeartbeat(PEER_ID);
            } catch (err) {
                console.error('[sendHeartbeat]', err);
            }
        }, 5000);
    
        // Cleanup interval on component destroy
        onDestroy(() => {
            clearInterval(interval);
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
