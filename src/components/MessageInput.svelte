<script lang="ts">
    // Props:
    export let onSend: (message: string) => void // Callback to send a message
    export let onSendFile: () => void // Callback to trigger a file sent dialog

    let message = '' // Bound to the text input value

    /** Called when the user clicks "Send" or presses Enter */
    const send = () => {
        if (message.trim()) {
        onSend(message)
        message = ''  // Clear input after send
        }
    }
</script>

<!-- Input area with text field, attach file button, and send button -->
<div class="input-box">
    <input
        bind:value={message}
        placeholder="Type a message..."
        on:keydown={(e) => e.key === 'Enter' && send()}
    />
    <!-- Button to open file picker -->
    <button on:click={onSendFile} title="Send a file">📎</button>
    <!-- Button to send text -->
    <button on:click={send}>Send</button>
</div>

<style>
    .input-box {
        display: flex;
        padding: 1rem;
        border-top: 1px solid #ccc;
        background: #fff;
    }
    input {
        flex: 1;
        margin-right: 0.5rem;
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    button {
        margin-left: 0.25rem;
        padding: 0.5rem 1rem;
        cursor: pointer;
        border: none;
        background-color: #007acc;
        color: white;
        border-radius: 4px;
    }
    button[title] {
        background-color: #6c757d;
    }
    button:hover {
        opacity: 0.9;
    }
</style>
