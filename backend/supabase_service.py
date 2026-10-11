"""
Supabase Backend Service:
REST API client for global Leaderboards, User Profiles, and Survivor Rescue Badges.
Includes seamless offline fallback caching.
"""
import json
import os
import time
import urllib.request
import urllib.error


class SupabaseService:
    def __init__(self, config_path="backend_config.json"):
        self.config_path = config_path
        self.cache_path = "supabase_local_cache.json"
        self.supabase_url = ""
        self.supabase_key = ""
        self.is_connected = False

        self.load_config()
        self.load_cache()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.supabase_url = data.get("supabase_url", "").rstrip("/")
                    self.supabase_key = data.get("supabase_key", "")
            except Exception as e:
                print(f"Error reading Supabase config: {e}")

    def load_cache(self):
        """Loads offline cached leaderboards and badges."""
        default_leaderboard = {
            "1": [
                {"username": "GhostOperative", "clear_time_seconds": 42.5, "zombies_killed": 9},
                {"username": "Vance_Actual", "clear_time_seconds": 48.2, "zombies_killed": 8},
                {"username": "ZombieHunter99", "clear_time_seconds": 55.0, "zombies_killed": 7},
            ],
            "2": [
                {"username": "SubwaySurfer", "clear_time_seconds": 61.3, "zombies_killed": 11},
                {"username": "ShadowSniper", "clear_time_seconds": 72.0, "zombies_killed": 9},
            ],
            "3": [
                {"username": "DeltaLeader", "clear_time_seconds": 78.4, "zombies_killed": 14},
            ],
            "4": [
                {"username": "HazmatPro", "clear_time_seconds": 92.1, "zombies_killed": 16},
            ],
            "5": [
                {"username": "ApexSurvivor", "clear_time_seconds": 105.8, "zombies_killed": 19},
            ],
        }
        self.cache = {
            "leaderboards": default_leaderboard,
            "profiles": {},
            "badges": {},
            "pending_sync": []
        }
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    cached = json.load(f)
                    self.cache.update(cached)
            except Exception as e:
                print(f"Error loading local Supabase cache: {e}")

    def save_cache(self):
        try:
            with open(self.cache_path, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving Supabase cache: {e}")

    def _http_request(self, endpoint, method="GET", payload=None):
        if not self.supabase_url or not self.supabase_key:
            return None
        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        data_bytes = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=4) as response:
                res_body = response.read().decode("utf-8")
                return json.loads(res_body) if res_body else {}
        except Exception as e:
            # Network issue or invalid credentials: fall back to offline cache
            return None

    def get_leaderboard(self, level_id):
        """Fetch fastest level clearance times."""
        lvl_key = str(level_id)
        # Try live REST API
        remote_data = self._http_request(f"level_leaderboards?level_id=eq.{level_id}&order=clear_time_seconds.asc&limit=10")
        if remote_data is not None and isinstance(remote_data, list):
            self.is_connected = True
            return remote_data

        # Fallback to offline cached leaderboard
        return self.cache["leaderboards"].get(lvl_key, [])

    def submit_score(self, user_id, username, level_id, clear_time_seconds, zombies_killed):
        """Submit a completed mission clearance record."""
        lvl_key = str(level_id)
        entry = {
            "user_id": user_id,
            "username": username,
            "level_id": level_id,
            "clear_time_seconds": round(clear_time_seconds, 1),
            "zombies_killed": zombies_killed,
            "timestamp": int(time.time())
        }

        # 1. Update local cache immediately
        if lvl_key not in self.cache["leaderboards"]:
            self.cache["leaderboards"][lvl_key] = []
        self.cache["leaderboards"][lvl_key].append(entry)
        self.cache["leaderboards"][lvl_key].sort(key=lambda x: x["clear_time_seconds"])
        self.cache["leaderboards"][lvl_key] = self.cache["leaderboards"][lvl_key][:10]
        self.save_cache()

        # 2. Try online sync
        remote_res = self._http_request("level_leaderboards", method="POST", payload=entry)
        if remote_res is None:
            self.cache["pending_sync"].append({"endpoint": "level_leaderboards", "payload": entry})
            self.save_cache()
            return False
        return True

    def award_survivor_badge(self, user_id, level_id, survivor_name):
        """Unlock and save survivor rescue badge."""
        badge_map = {
            1: ("CADUCEUS_BADGE", "Field Doctor Rescued", "Extracted Dr. Sarah Chen from Outpost Medical Bay."),
            2: ("CIRCUIT_BREAKER", "Power Grid Restored", "Extracted Marcus Vance from Abandoned Subway."),
            3: ("PATHFINDER_BADGE", "Recon Telemetry Acquired", "Extracted Sergeant Ramos from City Barricade."),
            4: ("ANTIDOTE_HARVESTER", "Vaccine Formula Secured", "Extracted Dr. Elena Rostova from Chemical Plant."),
            5: ("APOCALYPSE_SAVIOR", "Master Antidote Dispersed", "Extracted Dr. Arthur Sterling from Sub-level Lab."),
        }
        b_info = badge_map.get(level_id, ("BADGE", "Survivor Rescued", "Rescued survivor."))
        badge_data = {
            "user_id": user_id,
            "level_id": level_id,
            "badge_id": b_info[0],
            "title": b_info[1],
            "description": b_info[2],
            "unlocked_at": int(time.time())
        }

        # Cache locally
        if user_id not in self.cache["badges"]:
            self.cache["badges"][user_id] = []
        if not any(b["badge_id"] == b_info[0] for b in self.cache["badges"][user_id]):
            self.cache["badges"][user_id].append(badge_data)
            self.save_cache()

            # Attempt REST sync
            self._http_request("rescue_badges", method="POST", payload=badge_data)
        return badge_data

    def get_badges(self, user_id):
        return self.cache["badges"].get(user_id, [])
