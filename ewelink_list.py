import requests
import os
import uuid
import time
import json
from dotenv import load_dotenv

def list_ewelink_devices():
    load_dotenv(override=True)
    
    app_id = (os.getenv("EWELINK_APP_ID") or "").strip()
    at = (os.getenv("EWELINK_ACCESS_TOKEN") or "").strip()
    # We found earlier you are in the 'as' region
    region = "as"
    
    if not at:
        print("Error: No access token found in .env. Please run ewelink_full_auth.py first.")
        return

    url = f"https://{region}-apia.coolkit.cc/v2/device/thing"
    
    nonce = str(uuid.uuid4())[:8]
    seq = str(int(time.time() * 1000))
    
    headers = {
        "X-Ck-Appid": app_id,
        "X-Ck-Nonce": nonce,
        "X-Ck-Seq": seq,
        "Authorization": f"Bearer {at}",
        "Content-Type": "application/json"
    }

    print(f"Fetching device list from {url}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("error") == 0:
            thing_list = data["data"]["thingList"]
            print(f"\n{'Name':<25} | {'Device ID':<15} | {'Online':<8} | {'UIID'}")
            print("-" * 65)
            
            for thing in thing_list:
                item = thing["itemData"]
                name = item.get("name", "Unknown")
                deviceid = item.get("deviceid", "N/A")
                online = "YES" if item.get("online") else "NO"
                uiid = item.get("extra", {}).get("extra", {}).get("uiid", "N/A")
                
                print(f"{name:<25} | {deviceid:<15} | {online:<8} | {uiid}")
            
            print("-" * 65 + "\n")
            return thing_list
        else:
            print(f"Error fetching devices: {data.get('msg')} (Code: {data.get('error')})")
            return None
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    list_ewelink_devices()
