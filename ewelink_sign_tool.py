import hmac
import hashlib
import base64
import json
import time
import uuid
import os
from dotenv import load_dotenv

def get_ewelink_signature(secret, message):
    """
    Core signature function: HMAC-SHA256 + Base64
    """
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

def generate_v2_signature_tool():
    load_dotenv(override=True)
    
    app_id = (os.getenv("EWELINK_APP_ID") or "").strip()
    app_secret = (os.getenv("EWELINK_APP_SECRET") or "").strip()
    
    if not app_id or not app_secret:
        print("Error: EWELINK_APP_ID or EWELINK_APP_SECRET missing in .env")
        return

    seq = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())[:8]

    print("\n" + "="*60)
    print("EWELINK V2 SIGNATURE TOOL")
    print("="*60)
    print(f"AppID: {app_id}")
    print(f"Seq:   {seq}")
    print(f"Nonce: {nonce}")
    print("-" * 60)

    # TYPE 1: SIGNATURE FOR OAUTH LOGIN / INITIAL GET (ID_SEQ)
    # used in Authorization header for GET /v2/user/oauth/code
    msg_id_seq = f"{app_id}_{seq}"
    sign_id_seq = get_ewelink_signature(app_secret, msg_id_seq)
    print(f"SIGNATURE (ID+SEQ): {sign_id_seq}")
    print(f"Header usage: Authorization: Sign {sign_id_seq}")

    print("-" * 60)

    # TYPE 2: SIGNATURE FOR POST BODY (Compact JSON)
    # Example for /v2/user/oauth/token or /v2/user/login
    test_body = {
        "clientId": app_id,
        "grantType": "authorization_code",
        "redirectUrl": "http://127.0.0.1"
    }
    
    # MUST use separators=(',', ':') for compact JSON
    compact_body = json.dumps(test_body, separators=(',', ':'))
    sign_body = get_ewelink_signature(app_secret, compact_body)
    
    print("EXAMPLE FOR BODY SIGNATURE:")
    print(f"Body: {compact_body}")
    print(f"SIGNATURE (BODY): {sign_body}")
    print(f"Header usage: Authorization: Sign {sign_body}")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_v2_signature_tool()
