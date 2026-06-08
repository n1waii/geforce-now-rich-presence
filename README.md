# GeForce NOW Rich Presence for Discord (macOS Native)

<div align="center">
  <img width="208" alt="App Menu Bar Screenshot" src="https://github.com/user-attachments/assets/d6fe1370-9a80-4cb6-8967-b39b40ead46e" />
  <img width="212" alt="Discord Rich Presence Screenshot" src="https://github.com/user-attachments/assets/c7bb586f-a688-41a5-bc13-fae1b4a07961" />
</div>

A lightweight, native macOS menu bar application that automatically updates your Discord Rich Presence to show the game you are currently streaming via NVIDIA GeForce NOW. 

> **Note:** This application is built strictly for **macOS**. If you are looking for a Windows alternative, check out the original inspiration for this project: [KarmaDevz/GeForce-NOW-Rich-Presence](https://github.com/KarmaDevz/GeForce-NOW-Rich-Presence).

---

## Features

* **Native Menu Bar UI:** Runs silently in your Mac's top menu bar. Click the icon to instantly toggle your Discord presence on or off.
* **Zero-Lag File Tailing:** Uses extremely lightweight, memory-safe file pointers to read GeForce NOW logs in real-time without consuming CPU or RAM.
* **State Tracking:** Automatically self-heals and re-hooks if the NVIDIA app crashes, restarts, or wipes its own log files.

---

## Installation 

1. Head over to the **[Releases](../../releases/latest)** page and download the latest `main.app.zip` (or `GeForceNowPresence.app.zip`) file.
2. Double-click the `.zip` file in your Downloads folder to extract the application.
3. Drag the extracted `.app` file into your Mac's **Applications** folder and run it.
You will now see a "GFN" icon on your MacOS topbar. 
<img width="1512" height="30" alt="Screenshot 2026-05-22 at 6 49 34 PM" src="https://github.com/user-attachments/assets/2fa0ea41-1d86-45e3-b307-8e5c0c93529e" />
<img width="175" height="140" alt="Screenshot 2026-05-22 at 6 49 59 PM" src="https://github.com/user-attachments/assets/406d13c7-50b6-4f0c-b763-34c0a90fcda2" />

(Alternatively, you can build the app yourself by running the build_app.sh file.)


### ⚠️ macOS Gatekeeper Warning ("Unidentified Developer")
Because this app is open-source and not signed with a paid Apple Developer certificate, macOS will block it the first time you try to open it by double-clicking. 

**To open it safely:**
1. **Right-click** (or `Control` + Click) the app icon in your Finder.
2. Select **Open** from the drop-down menu.
3. Click **Open** again on the security warning popup. 
*(You only need to do this once. After that, it will open normally!)*

--

## Troubleshooting & Logs

If your game is still not detected, make sure to disable the default NVIDIA GFN Rich Presence by going to GFN settings.

Because this application runs entirely headlessly as a background UI element, standard errors are hidden by macOS. 

If your Discord presence isn't updating or the app behaves strangely, you can easily view the live diagnostic logs by opening your Mac's built-in **Console** app, or by running this command in your Terminal:

```bash
tail -f ~/Library/Logs/GFN_Presence/gfn_presence_debug.log


