<script lang="ts">
    import type { Message } from './types'

    // Props:
    export let messages: Message[] = []  // Array of messages to display
</script>

<!-- Scrollable area showing all messages -->
<section class="chat-window">
    {#each messages as msg}
        <div class="{msg.from === 'me' ? 'outgoing' : 'incoming'}">
        <!-- Display message content -->
        <p>{msg.content}</p>
        </div>
    {/each}
</section>

<style>
    .chat-window {
        padding: 1rem;
        flex: 1;
        overflow-y: auto;
        background-color: #fafafa;
    }
    .incoming {
        text-align: left;
        margin-bottom: 0.5rem;
    }
    .outgoing {
        text-align: right;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    p {
        display: inline-block;
        padding: 0.5rem;
        border-radius: 4px;
        background: #e0e0e0;
        max-width: 70%;
    }
    .outgoing p {
        background: #cfe9ff;
    }
</style>
