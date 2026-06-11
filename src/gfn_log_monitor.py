import os
import json
import re
import subprocess


class GFNLogMonitor:
    GAME_CLOSED_MARKERS = (
        "source onFocus for key Library",
        "onFocus for key SessionChange",
        "UdsEndOfSessionReport",
        '"source":"EndOfSession"',
        "sessionEndTimeStamp",
    )

    def __init__(self, config_path="games_config_merged.json"):
        self.log_path = os.path.expanduser('~/Library/Application Support/NVIDIA/GeForceNOW/console.log')
        self.file_handle = None
        self.current_game = "GeForce NOW Dashboard"
        self.is_playing = False
        
        self.game_mappings = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.game_mappings = json.load(f)
                print(f"Successfully loaded {len(self.game_mappings)} game configurations from JSON!")
            except Exception as e:
                print(f"Error loading JSON configuration file: {e}")
 
    def sanitize_string(self, text):
        if not text:
            return ""
        clean = text.replace("®", "").replace("™", "")
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def init_stream(self, seek_to_end=True):
        """Locks onto the log file."""
        if self.file_handle:
            try: self.file_handle.close()
            except: pass
        
        if os.path.exists(self.log_path):
            try:
                self.file_handle = open(self.log_path, 'r', encoding='utf-8', errors='ignore')
                if seek_to_end:
                    self.file_handle.seek(0, os.SEEK_END)
                return True
            except Exception as e:
                print(f"[Log Monitor Error]: {e}")
                self.file_handle = None
        return False

    def check_file_rotated(self):
        """Standard OS check to see if NVIDIA deleted and recreated the log file."""
        try:
            path_inode = os.stat(self.log_path).st_ino
            fd_inode = os.fstat(self.file_handle.fileno()).st_ino
            return path_inode != fd_inode
        except Exception:
            return True # File was deleted by NVIDIA

    def reset(self):
        print("[Log Monitor]: Resetting states...")
        self.current_game = "GeForce NOW Dashboard"
        self.is_playing = False

    def mark_game_closed(self):
        if self.is_playing:
            print(f"[Event Trigger]: {self.current_game} closed. Returning to Dashboard.")
            self.current_game = "GeForce NOW Dashboard"
            self.is_playing = False

    def close(self):
        if self.file_handle:
            try: self.file_handle.close()
            except: pass
            self.file_handle = None

    def scan_new_lines(self):
        if not self.file_handle:
            # Read the existing log once on startup so games that were launched
            # before this app started are detected too.
            if not self.init_stream(seek_to_end=False):
                return self.current_game, self.is_playing
        elif self.check_file_rotated():
            print("[Log Monitor]: NVIDIA restarted. Re-hooking fresh stream...")
            self.init_stream(seek_to_end=False)

        try:
            lines = self.file_handle.readlines()
        except Exception as e:
            print(f"[Log Monitor]: Stream read error ({e}).")
            self.close()
            return self.current_game, self.is_playing
        
        if lines:
            for line in lines:
                if "ApplicationClass" in line and "Launch game" in line:
                    match = re.search(r'Launch game\s+(.*?)\s+\[', line)
                    if match:
                        raw_name = match.group(1).strip()
                        self.current_game = self.sanitize_string(raw_name)
                        self.is_playing = True
                        print(f"[Event Trigger]: Launched {self.current_game}")
                
                elif any(marker in line for marker in self.GAME_CLOSED_MARKERS):
                    self.mark_game_closed()

        return self.current_game, self.is_playing
