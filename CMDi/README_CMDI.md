# 🧨 Command Injection Payload Generator

This is a standalone Python module that generates payloads specifically for testing **Command Injection (CMDi)** vulnerabilities in web applications.

It supports:
- Linux & Windows payloads
- Base64 encoding
- Copying to clipboard
- Exporting to `.txt` or `.json` files

---

## 🔧 Features

- 🛠 Generates a list of common command injection payloads
- 🔐 Supports optional **Base64 encoding**
- 📋 Can **copy payloads to clipboard**
- 📁 Can **export payloads to file** (`.txt` or `.json`)

---

## 💻 Example Payloads Generated

- `; whoami`
- `&& whoami`
- `| whoami`
- `` `whoami` ``
- `$(whoami)`
- `&& net user`
- `ping -c 1 127.0.0.1`

---

## 🚀 Usage

```bash
python cmdi_tool.py --cmd
```

### Optional Flags:

| Flag | Description |
|------|-------------|
| `--cmd`         | Generate CMDi payloads (required) |
| `--encode base64` | Encode payloads in Base64 |
| `--copy`        | Copy payloads to clipboard |
| `--export txt`  | Save to `cmdi_payloads.txt` |
| `--export json` | Save to `cmdi_payloads.json` |

---

### 🔹 Example Commands

#### Show payloads in terminal:
```bash
python cmdi_tool.py --cmd
```

#### Export to text file:
```bash
python cmdi_tool.py --cmd --export txt
```

#### Encode in Base64 and copy:
```bash
python cmdi_tool.py --cmd --encode base64 --copy
```

---

## 🔌 Integration Guide (for full tool with XSS/SQLi/etc.)

To integrate this into a unified `payloadgen.py`:

1. Copy the `cmd_payloads` list into your shared payload section.
2. In the argument parser section, keep:
```python
parser.add_argument('--cmd', action='store_true', help='Generate Command Injection payloads')
```
3. Add this to your shared generation logic:
```python
if args.cmd:
    for payload in cmd_payloads:
        final_payload = payload
        if args.encode:
            final_payload = encode_payload(final_payload, args.encode)
        generated_payloads.append(final_payload)
```

✅ It will now work alongside `--xss` and `--sqli`.

---

## ⚠️ Legal Note

This tool is intended **only for ethical testing and educational purposes** on systems you own or have explicit permission to test.

Using it on unauthorized targets is illegal and unethical.

---

## 👨‍💻 Author

**Mohsin Sheikh**  
Contributors:
**Obaid ur Rehman Uppal**
**Abdullah**
Cybersecurity Intern — ITSOLERA Pvt Ltd  
