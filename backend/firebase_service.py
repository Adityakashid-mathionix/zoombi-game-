"""
Firebase Backend Service:
Firebase Auth (Anonymous & Email/Password) and Realtime Database / Firestore sync.
Features offline persistent caching for unlocked levels, equipment, currency, and stats.
"""
import json
import os
import time
import urllib.request
import urllib.error
import uuid


class FirebaseService:
    def __init__(self, config_path="backend_config.json"):
        self.config_path = config_path
        self.cache_path = "firebase_local_cache.json"
        self.api_key = ""
        self.db_url = ""

        self.current_user = None
        self.is_logged_in = False
        self.is_connected = False

        self.load_config()
        self.load_cache()
        self.auto_login()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.api_key = data.get("firebase_api_key", "")
                    self.db_url = data.get("firebase_db_url", "").rstrip("/")
            except Exception as e:
                print(f"Error loading Firebase config: {e}")

    def load_cache(self):
        self.cache = {
            "user_id": f"anon_{uuid.uuid4().hex[:8]}",
            "username": "Operative_Vance",
            "email": "",
            "is_anonymous": True,
            "unlocked_levels": [1],  # Level 1 unlocked by default
            "currency": 500,  # Quarantine credits
            "loadout": {
                "primary_weapon": "shotgun",
                "tactical_item": "medkit"
            },
            "stats": {
                "total_kills": 0,
                "survivors_rescued": 0,
                "missions_completed": 0,
                "best_times": {}
            }
        }
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    saved = json.load(f)
                    self.cache.update(saved)
            except Exception as e:
                print(f"Error loading Firebase cache: {e}")

    def save_cache(self):
        try:
            with open(self.cache_path, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving Firebase cache: {e}")

    def auto_login(self):
        """Auto signs in anonymously or restores persistent session."""
        if not self.api_key:
            # Running in local offline authenticated mode
            self.current_user = {
                "uid": self.cache["user_id"],
                "email": self.cache["email"],
                "display_name": self.cache["username"],
                "is_anonymous": self.cache["is_anonymous"]
            }
            self.is_logged_in = True
            return

        # Attempt anonymous sign-in via Firebase Auth REST API
        self.sign_in_anonymously()

    def sign_in_anonymously(self):
        if not self.api_key:
            return False
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        body = json.dumps({"returnSecureToken": True}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                self.current_user = {
                    "uid": res_data.get("localId", self.cache["user_id"]),
                    "id_token": res_data.get("idToken", ""),
                    "is_anonymous": True,
                    "display_name": self.cache["username"]
                }
                self.cache["user_id"] = self.current_user["uid"]
                self.cache["is_anonymous"] = True
                self.is_logged_in = True
                self.is_connected = True
                self.save_cache()
                self.pull_remote_data()
                return True
        except Exception:
            # Fallback to local session
            self.current_user = {
                "uid": self.cache["user_id"],
                "is_anonymous": True,
                "display_name": self.cache["username"]
            }
            self.is_logged_in = True
            return False

    def sign_in_email(self, email, password):
        if not self.api_key:
            # Update local offline session
            self.cache["email"] = email
            self.cache["username"] = email.split("@")[0]
            self.cache["is_anonymous"] = False
            self.current_user = {
                "uid": self.cache["user_id"],
                "email": email,
                "display_name": self.cache["username"],
                "is_anonymous": False
            }
            self.save_cache()
            return True

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        body = json.dumps({"email": email, "password": password, "returnSecureToken": True}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                self.current_user = {
                    "uid": res_data.get("localId"),
                    "email": email,
                    "id_token": res_data.get("idToken"),
                    "display_name": email.split("@")[0],
                    "is_anonymous": False
                }
                self.cache["user_id"] = self.current_user["uid"]
                self.cache["email"] = email
                self.cache["username"] = self.current_user["display_name"]
                self.cache["is_anonymous"] = False
                self.is_logged_in = True
                self.is_connected = True
                self.save_cache()
                self.pull_remote_data()
                return True
        except Exception as e:
            print(f"Firebase email login error: {e}")
            return False

    def pull_remote_data(self):
        """Fetch saved player progress from Firebase Realtime DB."""
        if not self.db_url or not self.current_user or "id_token" not in self.current_user:
            return
        uid = self.current_user["uid"]
        token = self.current_user.get("id_token")
        url = f"{self.db_url}/players/{uid}.json?auth={token}"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode("utf-8"))
                if data and isinstance(data, dict):
                    self.cache.update(data)
                    self.save_cache()
        except Exception:
            pass

    def push_remote_data(self):
        """Sync player progress up to Firebase Realtime DB."""
        if not self.db_url or not self.current_user or "id_token" not in self.current_user:
            return False
        uid = self.current_user["uid"]
        token = self.current_user.get("id_token")
        url = f"{self.db_url}/players/{uid}.json?auth={token}"
        body = json.dumps(self.cache).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=body, headers=headers, method="PUT")
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                self.is_connected = True
                return True
        except Exception:
            return False

    def unlock_next_level(self, completed_level_id):
        from engine.settings import LEVELS_DATA
        next_lvl = completed_level_id + 1
        max_level = len(LEVELS_DATA)
        if next_lvl <= max_level and next_lvl not in self.cache["unlocked_levels"]:
            self.cache["unlocked_levels"].append(next_lvl)
            self.cache["unlocked_levels"].sort()
        # Reward currency
        self.cache["currency"] += 250
        self.cache["stats"]["missions_completed"] += 1
        self.cache["stats"]["survivors_rescued"] += 1
        self.save_cache()
        self.push_remote_data()

    def record_kill(self):
        self.cache["stats"]["total_kills"] += 1
        self.cache["currency"] += 10
        self.save_cache()

    def set_loadout(self, primary_weapon, tactical_item):
        self.cache["loadout"]["primary_weapon"] = primary_weapon
        self.cache["loadout"]["tactical_item"] = tactical_item
        self.save_cache()
        self.push_remote_data()
