<script lang="ts">
    import PeerList from '../components/PeerList.svelte';
    import ChatWindow from '../components/ChatWindow.svelte';
    import MessageInput from '../components/MessageInput.svelte';
    import type { Peer, Message } from '../components/types';
    import { fetchPeers, registerPeer, sendHeartbeat } from '../lib/api';
    import { onDestroy } from 'svelte';
    import { listen } from '@tauri-apps/api/event';
    import { invoke } from '@tauri-apps/api/core';

    // Reactive state
    let peerId = '';
    let listenPort: number | null = null;
    let connected = false;

    let peers: Peer[] = [];
    let selectedPeer: Peer | null = null;
    let messages: Message[] = [];
    let socketId: number | null = null;
    let heartbeatInterval: ReturnType<typeof setInterval>;
    let unlisten: () => void;

    async function loadPeers() {
        try {
        peers = await fetchPeers();
        } catch (err) {
        console.error('[loadPeers]', err);
        }
    }

    async function connect() {
        if (!peerId || !listenPort) return;
        // start Python listener on chosen port
        try {
        await invoke('init_listener', { port: listenPort });
        } catch (err) {
        console.error('[init_listener]', err);
        return;
        }

        // register with discovery server
        try {
        await registerPeer(peerId, listenPort);
        } catch (err) {
        console.error('[registerPeer]', err);
        return;
        }

        await loadPeers();

        // start heartbeat + refresh
        heartbeatInterval = setInterval(async () => {
        try {
            await sendHeartbeat(peerId);
            await loadPeers();
        } catch (err) {
            console.error('[heartbeat/loadPeers]', err);
        }
        }, 5000);

        // listen for inbound messages
        unlisten = await listen<{ sid: number; text: string }>(
        'chat-message',
        event => {
            const { sid, text } = event.payload;
            if (sid === socketId) {
            messages = [
                ...messages,
                { from: selectedPeer!.id, to: peerId, content: text, timestamp: new Date().toISOString() }
            ];
            }
        }
        );

        connected = true;
    }

    async function selectPeer(peer: Peer) {
        selectedPeer = peer;
        messages = [];
        try {
        socketId = await invoke<number>('start_chat', {
            peerIp: peer.ip,
            peerPort: peer.port,
            myId: peerId,
        });
        } catch (err) {
        console.error('[start_chat]', err);
        }
    }

    async function handleSend(content: string) {
        if (socketId === null) return;
        const outgoing: Message = { from: 'me', to: selectedPeer!.id, content, timestamp: new Date().toISOString() };
        messages = [...messages, outgoing];
        try {
        await invoke('send_message', { socketId, text: content });
        } catch (err) {
        console.error('[send_message]', err);
        }
    }

    function handleSendFile() {
        alert('File send not implemented yet.');
    }

    onDestroy(() => {
        clearInterval(heartbeatInterval);
        unlisten?.();
    });
</script>

<main class="app">
    {#if !connected}
        <div class="connect-form">
        <input placeholder="Your peer ID" bind:value={peerId} />
        <input
            type="number"
            placeholder="Listen port"
            bind:value={listenPort}
        />
        <button on:click={connect} disabled={!peerId || !listenPort}>
            Connect
        </button>
        </div>
    {:else}
        <!-- Sidebar of peers -->
        <PeerList {peers} onSelect={selectPeer} />

        <!-- Chat + input section -->
        <div class="chat-section">
        <ChatWindow {messages} />
        <MessageInput onSend={handleSend} onSendFile={handleSendFile} />
        </div>
    {/if}
</main>

<style>
    .app {
        display: flex;
        height: 100vh;
        font-family: sans-serif;
    }

    .connect-form {
        margin: auto;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .connect-form input,
    .connect-form button {
        padding: 0.5rem;
        font-size: 1rem;
    }

    .chat-section {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
</style>
