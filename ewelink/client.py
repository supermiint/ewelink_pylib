import hmac
import hashlib
import base64
import json
import time
import uuid
import os
import requests
from dotenv import load_dotenv, find_dotenv

class EwelinkClient:
    """
    eWeLink API V2 Client library wrapper.
    Handles HMAC signatures, OAuth logins, token persistence, and listing/controlling devices.
    """
    def __init__(self, app_id=None, app_secret=None, email=None, password=None, region="as", access_token=None, env_path=None):
        self.env_path = env_path or find_dotenv() or ".env"
        # Load environment variables if file exists
        if os.path.exists(self.env_path):
            load_dotenv(self.env_path, override=True)
            
        self.app_id = app_id or os.getenv("EWELINK_APP_ID", "").strip()
        self.app_secret = app_secret or os.getenv("EWELINK_APP_SECRET", "").strip()
        self.email = email or os.getenv("EWELINK_EMAIL", "").strip()
        self.password = password or os.getenv("EWELINK_PASSWORD", "").strip()
        self.region = region or os.getenv("EWELINK_REGION", "as").strip()
        self.access_token = access_token or os.getenv("EWELINK_ACCESS_TOKEN", "").strip()
        
    def _get_signature(self, message):
        if not self.app_secret:
            raise ValueError("App Secret is missing. Cannot generate signature.")
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
        
    def login(self):
        """
        Executes the two-step OAuth login flow:
        1. POST /v2/user/oauth/code to get auth code and user region
        2. POST /v2/user/oauth/token to get the access token
        Saves token to environment configuration file (.env) if present.
        """
        if not all([self.app_id, self.app_secret, self.email, self.password]):
            raise ValueError("App ID, App Secret, Email, and Password are all required for login.")
            
        host = f"{self.region}-apia.coolkit.cc"
        
        # --- STEP 1: GET CODE ---
        nonce = str(uuid.uuid4())[:8]
        seq = str(int(time.time() * 1000))
        
        code_payload = {
            "email": self.email,
            "password": self.password,
            "clientId": self.app_id,
            "state": "random_state",
            "redirectUrl": "http://127.0.0.1",
            "grantType": "authorization_code"
        }
        
        compact_body_code = json.dumps(code_payload, separators=(',', ':'))
        # Using Type 1 Sign (appId_seq) for authorization header to get oauth code
        signature_headers = self._get_signature(f"{self.app_id}_{seq}")
        
        headers_code = {
            "X-Ck-Appid": self.app_id,
            "X-Ck-Nonce": nonce,
            "X-Ck-Seq": seq,
            "Authorization": f"Sign {signature_headers}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        url_code = f"https://{host}/v2/user/oauth/code"
        resp_code = requests.post(url_code, data=compact_body_code, headers=headers_code)
        resp_code.raise_for_status()
        data_code = resp_code.json()
        
        if data_code.get("error") != 0:
            raise RuntimeError(f"Failed to obtain authorization code: {data_code}")
            
        code = data_code["data"]["code"]
        self.region = data_code["data"]["region"]
        
        # --- STEP 2: EXCHANGE FOR TOKEN ---
        time.sleep(0.5) # small delay
        
        token_payload = {
            "code": code,
            "clientId": self.app_id,
            "clientSecret": self.app_secret,
            "grantType": "authorization_code",
            "redirectUrl": "http://127.0.0.1"
        }
        
        compact_body_token = json.dumps(token_payload, separators=(',', ':'))
        signature_token = self._get_signature(compact_body_token)
        
        headers_token = {
            "X-Ck-Appid": self.app_id,
            "X-Ck-Nonce": str(uuid.uuid4())[:8],
            "X-Ck-Seq": str(int(time.time() * 1000)),
            "Authorization": f"Sign {signature_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        url_token = f"https://{self.region}-apia.coolkit.cc/v2/user/oauth/token"
        resp_token = requests.post(url_token, data=compact_body_token, headers=headers_token)
        resp_token.raise_for_status()
        data_token = resp_token.json()
        
        if data_token.get("error") != 0:
            raise RuntimeError(f"Failed to exchange code for token: {data_token}")
            
        self.access_token = data_token["data"]["accessToken"]
        
        # Save to environment file
        self._save_to_env()
        
        return self.access_token

    def _save_to_env(self):
        """Helper to write or update environment variables in .env file."""
        lines = []
        if os.path.exists(self.env_path):
            with open(self.env_path, "r") as f:
                lines = f.readlines()
                
        keys_to_update = {
            "EWELINK_ACCESS_TOKEN": self.access_token,
            "EWELINK_REGION": self.region
        }
        
        new_lines = []
        updated_keys = set()
        for line in lines:
            stripped = line.strip()
            if stripped and "=" in stripped:
                key = stripped.split("=")[0].strip()
                if key in keys_to_update:
                    new_lines.append(f"{key}={keys_to_update[key]}\n")
                    updated_keys.add(key)
                    continue
            new_lines.append(line)
            
        for key, val in keys_to_update.items():
            if key not in updated_keys:
                if new_lines and not new_lines[-1].endswith("\n"):
                    new_lines.append("\n")
                new_lines.append(f"{key}={val}\n")
                
        with open(self.env_path, "w") as f:
            f.writelines(new_lines)
            
    def _get_headers(self):
        if not self.access_token:
            raise ValueError("Access token is missing. Please run login() or provide a token.")
        return {
            "X-Ck-Appid": self.app_id,
            "X-Ck-Nonce": str(uuid.uuid4())[:8],
            "X-Ck-Seq": str(int(time.time() * 1000)),
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def list_devices(self):
        """Fetch the list of registered devices."""
        url = f"https://{self.region}-apia.coolkit.cc/v2/device/thing"
        headers = self._get_headers()
        
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("error") != 0:
            raise RuntimeError(f"Error fetching device list: {data.get('msg')} (Code: {data.get('error')})")
            
        return data["data"]["thingList"]

    def get_device(self, device_id):
        """Find a specific device from the user list."""
        devices = self.list_devices()
        for d in devices:
            if d.get("itemData", {}).get("deviceid") == device_id:
                return d
        return None

    def control_device(self, device_id, state, outlet=None):
        """
        Turn a device ON or OFF.
        
        :param device_id: The unique eWeLink device ID
        :param state: 'on' or 'off' (case-insensitive)
        :param outlet: Optional switch outlet index (0, 1, ...) for multi-channel devices
        """
        state = state.lower()
        if state not in ("on", "off"):
            raise ValueError("State must be either 'on' or 'off'")
            
        url = f"https://{self.region}-apia.coolkit.cc/v2/device/thing/status"
        headers = self._get_headers()
        
        if outlet is not None:
            # Multi-channel switch format
            params = {
                "switches": [
                    {"switch": state, "outlet": int(outlet)}
                ]
            }
        else:
            # Single-channel switch format
            params = {
                "switch": state
            }
            
        payload = {
            "type": 1, # Type 1 means physical device / thing
            "id": device_id,
            "params": params
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("error") != 0:
            raise RuntimeError(f"Failed to control device: {data.get('msg')} (Code: {data.get('error')})")
            
        return data
