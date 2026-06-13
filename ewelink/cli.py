import argparse
import sys
import os
import json
from .client import EwelinkClient

def print_device_table(thing_list):
    print(f"\n{'Name':<25} | {'Device ID':<15} | {'Online':<8} | {'Type (UIID)':<12} | {'State'}")
    print("-" * 75)
    for thing in thing_list:
        item = thing.get("itemData", {})
        name = item.get("name", "Unknown")
        deviceid = item.get("deviceid", "N/A")
        online = "YES" if item.get("online") else "NO"
        uiid = item.get("extra", {}).get("extra", {}).get("uiid", "N/A")
        
        # Determine the current state from params if available
        params = item.get("params", {})
        state = "N/A"
        if "switch" in params:
            state = params["switch"].upper()
        elif "switches" in params:
            states = [f"#{sw.get('outlet')}:{sw.get('switch').upper()}" for sw in params["switches"]]
            state = ", ".join(states)
            
        print(f"{name:<25} | {deviceid:<15} | {online:<8} | {uiid:<12} | {state}")
    print("-" * 75 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="eWeLink Python CLI Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ewelink login
  ewelink list
  ewelink on 1000abc123
  ewelink off 1000abc123 --outlet 0
  ewelink status 1000abc123
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-commands")
    
    # login sub-command
    subparsers.add_parser("login", help="Log in to eWeLink using email and password and store access token in .env")
    
    # list sub-command
    subparsers.add_parser("list", help="List all registered eWeLink devices")
    
    # on sub-command
    on_parser = subparsers.add_parser("on", help="Turn a device on")
    on_parser.add_argument("device_id", help="Target device ID")
    on_parser.add_argument("--outlet", type=int, default=None, help="Outlet index for multi-channel devices")
    
    # off sub-command
    off_parser = subparsers.add_parser("off", help="Turn a device off")
    off_parser.add_argument("device_id", help="Target device ID")
    off_parser.add_argument("--outlet", type=int, default=None, help="Outlet index for multi-channel devices")
    
    # status sub-command
    status_parser = subparsers.add_parser("status", help="Get full status detail of a specific device")
    status_parser.add_argument("device_id", help="Target device ID")
    
    args = parser.parse_args()
    
    try:
        client = EwelinkClient()
    except Exception as e:
        print(f"Error initializing client: {e}")
        sys.exit(1)
        
    if args.command == "login":
        print("Starting eWeLink login flow...")
        try:
            token = client.login()
            print(f"Login successful! Region set to '{client.region}'.")
            print("Access Token stored in environment configurations.")
        except Exception as e:
            print(f"Login failed: {e}")
            sys.exit(1)
            
    elif args.command == "list":
        try:
            devices = client.list_devices()
            print_device_table(devices)
        except Exception as e:
            print(f"Failed to list devices: {e}")
            sys.exit(1)
            
    elif args.command in ("on", "off"):
        state = args.command
        try:
            print(f"Sending '{state.upper()}' command to device {args.device_id}" + 
                  (f" (Outlet {args.outlet})" if args.outlet is not None else "") + "...")
            client.control_device(args.device_id, state, outlet=args.outlet)
            print("Command executed successfully!")
        except Exception as e:
            print(f"Failed to control device: {e}")
            sys.exit(1)
            
    elif args.command == "status":
        try:
            device = client.get_device(args.device_id)
            if not device:
                print(f"Device with ID {args.device_id} not found.")
                sys.exit(1)
            print(json.dumps(device, indent=2))
        except Exception as e:
            print(f"Failed to get device status: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
