// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[tauri::command]
fn init_listener(port: u16) -> Result<(), String> {
    // Spawn `python chat_service.py listener 5001`
    std::process::Command::new("python")
        .arg("src/chat_service.py")
        .arg("listen")
        .arg(port.to_string())
        .spawn()
        .map_err(|e| format!("failed to launch listener: {}", e))?;
    Ok(())
}

#[tauri::command]
fn start_chat(
    peer_ip: String,
    peer_port: u16,
    my_id: String,
) -> Result<u32, String> {
    // Shell out to Python to call `start_chat(...)`, capture its socket ID
    let output = std::process::Command::new("python")
        .arg("src/chat_service.py")
        .arg("start")
        .arg(peer_ip)
        .arg(peer_port.to_string())
        .arg(my_id)
        .output()
        .map_err(|e| format!("failed to start chat: {}", e))?;
    if !output.status.success() {
        return Err(format!("chat_service error: {}", String::from_utf8_lossy(&output.stderr)));
    }
    // Python prints the socket ID on stdout
    let sid: u32 = String::from_utf8_lossy(&output.stdout)
        .trim()
        .parse()
        .map_err(|_| "invalid socket ID".to_string())?;
    Ok(sid)
}

#[tauri::command]
fn send_message(socket_id: u32, text: String) -> Result<(), String> {
    // Shell out to send a message
    let status = std::process::Command::new("python")
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
