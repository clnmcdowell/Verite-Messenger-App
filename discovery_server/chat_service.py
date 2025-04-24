import socket
import threading
from queue import Queue
from typing import Dict, Tuple

# Queue of incoming messages: each is (socket_id, text)
chat_queue: Queue[Tuple[int, str]] = Queue()

# Map of socket IDs → socket objects
open_sockets: Dict[int, socket.socket] = {}
_next_socket_id = 0  # auto-incrementing ID counter

def start_listener(port: int):
    """
    Start a background thread listening for incoming connections on `port`.
    Each accepted connection will spawn its own handler thread.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen()

    def accept_loop():
        while True:
            conn, _ = server.accept()
            threading.Thread(target=_handle_conn, args=(conn,), daemon=True).start()

    threading.Thread(target=accept_loop, daemon=True).start()


def _handle_conn(conn: socket.socket):
    """
    Handle an incoming peer connection.
    First we expect a CHAT_REQUEST or file data; then pass along to chat_queue.
    """
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            text = data.decode("utf-8", errors="ignore")
            chat_queue.put((0, text))  # 0 for “un-associated” incoming messages


def start_chat(peer_ip: str, peer_port: int, my_id: str) -> int:
    """
    Initiate a chat with another peer.
    Returns a socket_id you can use to send messages.
    Throws if peer declines.
    """
    global _next_socket_id

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((peer_ip, peer_port))

    # Send a chat request header
    s.sendall(f"CHAT_REQUEST:{my_id}".encode("utf-8"))
    response = s.recv(4096).decode("utf-8").strip()

    if response != "ACCEPT":
        s.close()
        raise RuntimeError("Chat declined by peer")

    # Assign an ID and store the socket
    socket_id = _next_socket_id
    _next_socket_id += 1
    open_sockets[socket_id] = s

    # Start a thread to push incoming messages from this socket into chat_queue
    def _receive_loop(sock: socket.socket, sid: int):
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chat_queue.put((sid, data.decode("utf-8", errors="ignore")))

    threading.Thread(target=_receive_loop, args=(s, socket_id), daemon=True).start()
    return socket_id


def send_message(socket_id: int, text: str):
    """
    Send a text message over the socket identified by `socket_id`.
    Raises if the socket is not found.
    """
    sock = open_sockets.get(socket_id)
    if not sock:
        raise KeyError(f"No open socket for ID {socket_id}")

    # Send the raw text
    sock.sendall(text.encode("utf-8"))
