<script lang="ts">
    import PeerList from '../components/PeerList.svelte';
    import ChatWindow from '../components/ChatWindow.svelte';
    import MessageInput from '../components/MessageInput.svelte';
    import type { Peer, Message } from '../components/types';

    // Currently selected peer (null = no selection)
    let selectedPeer: Peer | null = null

    // Dummy peer list for initial UI
    let peers: Peer[] = [
        { id: 'peer1', ip: '192.168.1.2', port: 5001 },
        { id: 'peer2', ip: '192.168.1.3', port: 5002 }
    ]

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
