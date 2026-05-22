# 🎮 GeForce NOW Rich Presence for Discord (macOS Native)

<div align="center">
  <img width="208" alt="App Menu Bar Screenshot" src="https://github.com/user-attachments/assets/d6fe1370-9a80-4cb6-8967-b39b40ead46e" />
  <img width="212" alt="Discord Rich Presence Screenshot" src="https://github.com/user-attachments/assets/c7bb586f-a688-41a5-bc13-fae1b4a07961" />
</div>

A lightweight, native macOS menu bar application that automatically updates your Discord Rich Presence to show the game you are currently streaming via NVIDIA GeForce NOW. 

> **Note:** This application is built strictly for **macOS**. If you are looking for a Windows alternative, check out the original inspiration for this project: [KarmaDevz/GeForce-NOW-Rich-Presence](https://github.com/KarmaDevz/GeForce-NOW-Rich-Presence).

---

## ✨ Features

* **Native Menu Bar UI:** Runs silently in your Mac's top menu bar. Click the icon to instantly toggle your Discord presence on or off.
* **Zero-Lag File Tailing:** Uses extremely lightweight, memory-safe file pointers to read GeForce NOW logs in real-time without consuming CPU or RAM.
* **Bulletproof State Tracking:** Automatically self-heals and re-hooks if the NVIDIA app crashes, restarts, or wipes its own log files.
* **Self-Cleaning Debug Logs:** Background application logs are automatically capped at 5MB using a standard rotation engine, ensuring it never bloats your hard drive.

---

## 🚀 Installation 

1. Head over to the **[Releases](../../releases/latest)** page and download the latest `main.app.zip` (or `GeForceNowPresence.app.zip`) file.
2. Double-click the `.zip` file in your Downloads folder to extract the application.
3. Drag the extracted `.app` file into your Mac's **Applications** folder.

Alternatively, you can build the app yourself by running the build_app.sh file.

### ⚠️ macOS Gatekeeper Warning ("Unidentified Developer")
Because this app is open-source and not signed with a paid Apple Developer certificate, macOS will block it the first time you try to open it by double-clicking. 

**To open it safely:**
1. **Right-click** (or `Control` + Click) the app icon in your Finder.
2. Select **Open** from the drop-down menu.
3. Click **Open** again on the security warning popup. 
*(You only need to do this once. After that, it will open normally!)*

---

## ⚙️ How It Works

Using the expansive database from [KarmaDevz's games_config_merged.json](https://github.com/KarmaDevz/GeForce-NOW-Rich-Presence/blob/master/config/games_config_merged.json), the application maps the internal string IDs of GeForce NOW games directly to specific Discord Application Client IDs.

Anytime you launch a game, the background engine:
1. Monitors your Mac's internal NVIDIA console stream (`~/Library/Application Support/NVIDIA/GeForceNOW/console.log`).
2. Detects the `Launch game` trigger and sanitizes the game title.
3. Cross-references the title with the JSON mapping database.
4. Pushes an instant IPC update to your local Discord desktop client.
5. Monitors for the `onFocus SessionChange` flag to know exactly when you quit the stream, cleanly dropping your status back to the "GeForce NOW Dashboard".

---

## 🛠️ Troubleshooting & Logs

Because this application runs entirely headlessly as a background UI element, standard errors are hidden by macOS. 

If your Discord presence isn't updating or the app behaves strangely, you can easily view the live diagnostic logs by opening your Mac's built-in **Console** app, or by running this command in your Terminal:

```bash
tail -f ~/Library/Logs/GFN_Presence/gfn_presence_debug.log
