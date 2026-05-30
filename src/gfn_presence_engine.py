import os
import json
import subprocess
import time
from pypresence import Presence
from src.gfn_log_monitor import GFNLogMonitor

class GFNPresenceEngine:
    def __init__(self, config_path="games_config_merged.json", default_id="YOUR_DEFAULT_APP_CLIENT_ID"):
        self.default_id = default_id
        self.active_status = None
        self.start_time = None
        self.rpc = None
        
        self.monitor = GFNLogMonitor()
        
        self.game_mappings = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.game_mappings = json.load(f)

    def compute_state(self):
        """Runs a tick evaluation step. Returns (game_name, display_status_text)."""
        current_game, is_playing = self.monitor.scan_new_lines()
        
        try:
            check_launcher = subprocess.run(['pgrep', '-x', 'GeForceNOW'], capture_output=True, text=True)
            check_streamer = subprocess.run(['pgrep', '-x', 'GeForceNOWStreamer'], capture_output=True, text=True)
            
            if not check_launcher.stdout.strip() and not check_streamer.stdout.strip():
                if self.active_status is not None:
                    print("[Engine Update]: GeForce NOW processes completely closed. Disconnecting.")
                    self.disconnect()
                return None, "Status: App Closed"
                
        except Exception as e:
            print(f"Process check fallback exception: {e}")
            pass

        if current_game != self.active_status:
            self.active_status = current_game
            self.start_time = int(time.time())

            print(f"[Engine Update]: Detected status change to '{self.active_status}'. Updating presence...")

            if self.rpc:
                try:
                    self.rpc.clear()
                    self.rpc.close()
                except Exception:
                    pass
                finally:
                    self.rpc = None
                
            if self.active_status in self.game_mappings:
                target_id = self.game_mappings[self.active_status]["client_id"]
            else:
                target_id = self.default_id
                
            try:
                self.rpc = Presence(target_id)
                self.rpc.connect()
                
                if self.active_status == "GeForce NOW Dashboard":
                    self.rpc.update(details="Browsing Games", state="In Launcher", start=self.start_time)
                else:
                    self.rpc.update(start=self.start_time)

            except Exception as e:
                print(f"Discord IPC bind error: {e}")
                self.rpc = None

        if self.active_status == "GeForce NOW Dashboard":
            return self.active_status, "Status: Browsing Launcher"
        return self.active_status, f"Playing: {self.active_status}"

    def disconnect(self):
        """Forcefully and instantly severs connections without blocking the UI thread."""
        if self.rpc:
            try:
                self.rpc.clear()
            except Exception:
                pass
                
            try:
                self.rpc.close()
            except Exception:
                pass
            finally:
                self.rpc = None
                
        self.active_status = None
        
        try:
            self.monitor.reset()
        except Exception as e:
            print(f"Error resetting log monitor: {e}")
            pass
            
    def re_enable(self):
        """Reset state so presence can reconnect on the next timer tick."""
        self.disconnect()
        
        
