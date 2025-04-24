// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{
    io::{BufRead, BufReader},
    process::{Command, Stdio},
    thread,
};
use tauri::{Manager, Emitter, WebviewWindow};

// Tauri command to start chat
#[tauri::command]
fn start_chat(
    peer_ip: String,
    peer_port: u16,
    my_id: String,
) -> Result<u32, String> {
    // Shell out to Python to call `start_chat(...)`, capture its socket ID
    let output = Command::new("python")
        .arg("src/chat_service.py")
        .arg("start")
        .arg(peer_ip)
        .arg(peer_port.to_string())
        .arg(my_id)
        .output()
        .map_err(|e| format!("failed to start chat: {}", e))?;
    if !output.status.success() {
        return Err(format!(
            "chat_service error: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }
    // Python prints the socket ID on stdout
    let sid: u32 = String::from_utf8_lossy(&output.stdout)
        .trim()
        .parse()
        .map_err(|_| "invalid socket ID".to_string())?;
    Ok(sid)
}

// Tauri command to send message
#[tauri::command]
fn send_message(socket_id: u32, text: String) -> Result<(), String> {
    let status = Command::new("python")
        .arg("src/chat_service.py")
        .arg("send")
        .arg(socket_id.to_string())
        .arg(text)
        .status()
        .map_err(|e| format!("failed to send message: {}", e))?;
    if !status.success() {
        return Err("chat_service returned error".into());
    }
    Ok(())
}

// Tauri command to initialize listener on custom port
#[tauri::command]
fn init_listener(window: WebviewWindow, port: u16) {
    spawn_python_listener(window, port);
}

// Spawn the Python listener and pipe stdout into events
fn spawn_python_listener(window: WebviewWindow, port: u16) {
    thread::spawn(move || {
        let mut child = Command::new("python")
            .arg("src/chat_service.py")
            .arg("listen")
            .arg(port.to_string())
            .stdout(Stdio::piped())
            .spawn()
            .expect("failed to launch chat_service listener");

        let stdout = child.stdout.take().expect("no stdout");
        let reader = BufReader::new(stdout);

        for line in reader.lines() {
            if let Ok(raw) = line {
                if let Some((sid_str, text)) = raw.split_once(':') {
                    if let Ok(sid) = sid_str.parse::<u32>() {
                        window
                            .emit("chat-message", serde_json::json!({ "sid": sid, "text": text }))
                            .expect("failed to emit event");
                    }
                }
            }
        }
    });
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            init_listener,
            start_chat,
            send_message
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
