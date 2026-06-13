import hmac
import hashlib
import base64
import json
import time
import uuid
import requests
import os
from dotenv import load_dotenv

def get_signature(secret, message):
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

def run_full_oauth():
    load_dotenv(override=True)
    
    app_id = (os.getenv("EWELINK_APP_ID") or "").strip()
    app_secret = (os.getenv("EWELINK_APP_SECRET") or "").strip()
    email = (os.getenv("EWELINK_EMAIL") or "").strip()
    password = (os.getenv("EWELINK_PASSWORD") or "").strip()
    
    host = "as-apia.coolkit.cc"
    
    # --- STEP 1: GET CODE ---
    print("Step 1: Requesting OAuth Code...")
    nonce = str(uuid.uuid4())[:8]
    seq = str(int(time.time() * 1000))
    
    code_payload = {
        "email": email,
        "password": password,
        "clientId": app_id,
        "state": "random_123",
        "redirectUrl": "http://127.0.0.1",
        "grantType": "authorization_code"
    }
    
    # Sign based on Body for the POST /v2/user/oauth/code
    compact_body_code = json.dumps(code_payload, separators=(',', ':'))
    # NOTE: eWeLink V2 docs sometimes require signature on ID_SEQ for headers, 
    # but based on your capture, you used the ID_SEQ sign for Authorization.
    signature_headers = get_signature(app_secret, f"{app_id}_{seq}")
    
    headers_code = {
        "X-Ck-Appid": app_id,
        "X-Ck-Nonce": nonce,
        "X-Ck-Seq": seq,
        "Authorization": f"Sign {signature_headers}",
        "Content-Type": "application/json; charset=utf-8"
    }

    resp_code = requests.post(f"https://{host}/v2/user/oauth/code", data=compact_body_code, headers=headers_code)
    data_code = resp_code.json()
    
    if data_code.get("error") != 0:
        print(f"Failed to get code: {data_code}")
        return

    code = data_code["data"]["code"]
    region = data_code["data"]["region"]
    print(f"Success! Code obtained: {code[:8]}...")

    # --- STEP 2: EXCHANGE FOR TOKEN ---
    print("Step 2: Exchanging Code for Token...")
    time.sleep(0.5) # Tiny pause
    
    token_payload = {
        "code": code,
        "clientId": app_id,
        "clientSecret": app_secret,
        "grantType": "authorization_code",
        "redirectUrl": "http://127.0.0.1"
    }
    
    compact_body_token = json.dumps(token_payload, separators=(',', ':'))
    signature_token = get_signature(app_secret, compact_body_token)
    
    headers_token = {
        "X-Ck-Appid": app_id,
        "X-Ck-Nonce": str(uuid.uuid4())[:8],
        "X-Ck-Seq": str(int(time.time() * 1000)),
        "Authorization": f"Sign {signature_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    resp_token = requests.post(f"https://{region}-apia.coolkit.cc/v2/user/oauth/token", data=compact_body_token, headers=headers_token)
    data_token = resp_token.json()

    print(f"Token Response JSON: {data_token}")
    if data_token.get("error") == 0:
        at = data_token["data"]["accessToken"] # Try 'accessToken' if 'at' is missing
        print(f"FINAL SUCCESS! Access Token obtained: {at[:10]}...")
        
        # Save to .env
        with open(".env", "a") as f:
            f.write(f"\nEWELINK_ACCESS_TOKEN={at}")
        print("Token saved to .env.")
    else:
        print(f"Failed to get token: {data_token}")

if __name__ == "__main__":
    run_full_oauth()
