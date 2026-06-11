import os
import json
import subprocess
import time
import urllib.request
import threading
from pypresence import Presence
from src.gfn_log_monitor import GFNLogMonitor

class GFNPresenceEngine:
    def __init__(self, config_path="games_config_merged.json", default_id="YOUR_DEFAULT_APP_CLIENT_ID"):
        self.config_path = config_path
        self.default_id = default_id
        self.active_status = None
        self.start_time = None
        self.rpc = None
        self.api_checked_games = set()
        
        self.monitor = GFNLogMonitor()
        
        self.game_mappings = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.game_mappings = json.load(f)

        # Start background update from Discord API
        threading.Thread(target=self._update_config_from_api, daemon=True).start()

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
                
            target_id = self._get_or_fetch_game_id(self.active_status)
                
            try:
                self.rpc = Presence(target_id)
                self.rpc.connect()
                
                if self.active_status == "GeForce NOW Dashboard":
                    self.rpc.update(details="Browsing Games", state="In Launcher", start=self.start_time)
                else:
                    self.rpc.update(details=self.active_status, state="Streaming on GeForce NOW", start=self.start_time)

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
        
    def _get_or_fetch_game_id(self, game_name):
        """Looks up a game locally, falling back to Discord's Detectable API if missing."""
        if game_name in self.game_mappings:
            return self.game_mappings[game_name].get("client_id", self.default_id)
            
        if game_name in self.api_checked_games:
            return self.default_id
            
        self.api_checked_games.add(game_name)
        
        print(f"[Engine API]: Game '{game_name}' not found locally. Fetching Discord Detectable API...")
        try:
            req = urllib.request.Request(
                'https://discord.com/api/v8/applications/detectable',
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            for app in data:
                app_name = app.get("name", "")
                aliases = app.get("aliases", [])
                
                if app_name.lower() == game_name.lower() or any(a.lower() == game_name.lower() for a in aliases):
                    client_id = app.get("id")
                    if client_id:
                        print(f"[Engine API]: Found '{game_name}'! ID: {client_id}. Saving to local config.")
                        self.game_mappings[game_name] = {
                            "name": app_name,
                            "client_id": client_id
                        }
                        
                        try:
                            with open(self.config_path, 'w', encoding='utf-8') as f:
                                json.dump(self.game_mappings, f, indent=4)
                        except Exception as e:
                            print(f"[Engine API]: Failed to write back to config file: {e}")
                            
                        return client_id
            print(f"[Engine API]: Game '{game_name}' not found in Discord Detectable API either.")
        except Exception as e:
            print(f"[Engine API]: Failed to fetch from Discord API: {e}")
            
        return self.default_id

    def _update_config_from_api(self):
        """Fetches all detectable applications from Discord API and updates local config in the background."""
        print("[Engine API]: Starting background update of games config from Discord API...")
        try:
            req = urllib.request.Request(
                'https://discord.com/api/v8/applications/detectable',
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            updated = False
            for app in data:
                app_name = app.get("name")
                client_id = app.get("id")
                if not app_name or not client_id:
                    continue
                
                # Check name
                if app_name not in self.game_mappings:
                    self.game_mappings[app_name] = {
                        "name": app_name,
                        "client_id": client_id
                    }
                    updated = True
                
                # Check aliases
                for alias in app.get("aliases", []):
                    if alias not in self.game_mappings:
                        self.game_mappings[alias] = {
                            "name": app_name,
                            "client_id": client_id
                        }
                        updated = True
            
            if updated:
                print("[Engine API]: New games found in Discord API. Updating local games_config_merged.json...")
                try:
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        json.dump(self.game_mappings, f, indent=4)
                    print("[Engine API]: Local games config updated successfully.")
                except Exception as e:
                    print(f"[Engine API]: Failed to save updated config: {e}")
            else:
                print("[Engine API]: Local games config is already up to date.")
        except Exception as e:
            print(f"[Engine API]: Background config update failed: {e}")
