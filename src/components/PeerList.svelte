<script lang="ts">
    import type { Peer } from './types'

    // Props:
    export let peers: Peer[] // Array of known peers
    export let onSelect: (peer: Peer) => void // Callback when a peer is clicked
</script>

<!-- Sidebar listing all peers -->
<aside class="peer-list">
    <h3>Peers</h3>
    {#each peers as peer}
    <!-- Each peer is a button; clicking selects that peer -->
    <button on:click={() => onSelect(peer)}>
        {peer.id}
    </button>
    {/each}
</aside>

<style>
    /* Basic styling for the peer list sidebar */
    .peer-list {
        padding: 1rem;
        border-right: 1px solid #ccc;
        width: 200px;
    }
    button {
        display: block;
        width: 100%;
        margin: 0.25rem 0;
        padding: 0.5rem;
        text-align: left;
        background: none;
        border: none;
        cursor: pointer;
    }
    button:hover {
        background-color: #f0f0f0;
    }
</style>
