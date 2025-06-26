# 🎯 ITsolera-Hunt: Main.py Usage Guide

Welcome to the **ITsolera-Hunt** project!  
This guide covers how to use the colorful and powerful `Main.py` — your CLI gateway to security reconnaissance and testing modules.

---

## 🚀 Getting Started

Run the script using **Python 3**:

```bash
python3 Main.py [options]
```

---

## 🛠️ Command-Line Options

| Option             | Description                                                   | Example Usage                                  |
|--------------------|---------------------------------------------------------------|-------------------------------------------------|
| `--xssReflected`   | 🟠 Launches the **Reflected XSS** testing module.<br>Requires: `Module/ReconnResult/param_urls.txt` | `python3 Main.py --xssReflected`   |
| `--sqli`           | 🟣 Runs the **SQL Injection** generator module.                | `python3 Main.py --sqli`            |
| `--cmd`            | 🔵 Executes the **Command Injection** module.<br>Supports extra flags:<br>&nbsp;&nbsp;`--encode`<br>&nbsp;&nbsp;`--copy`<br>&nbsp;&nbsp;`--export` | `python3 Main.py --cmd --encode`    |

If you run it without a valid argument, it will show you all available options.

---

## 🌈 Example Scenarios

```bash
# Reflected XSS Testing
python3 Main.py --xssReflected

# SQL Injection Generator
python3 Main.py --sqli

# Command Injection with Encoding
python3 Main.py --cmd --encode
```

---

## 📂 File Structure & Requirements

- All modules and required files should be in their expected locations:
  - `Module/ReconnResult/param_urls.txt`
  - `Module/Reflected.py`
  - `Module/sqli_generator.py`
  - `CMDi/CMDi.py`
- The script uses subprocesses to run other Python scripts/modules.

---

## 💡 Tips

- Use colorful terminal themes for a better experience!
- Pipe the output to log files for further analysis.
- Make sure Python 3 is installed and all dependencies are met.

---

## 📝 Source

See the full script here: [`Main.py`](https://github.com/mostafa587/ITsolera-Hunt/blob/main/Main.py)

---

> Made with ❤️ by [mostafa587](https://github.com/mostafa587)  
> Level up your security hunting! 🚩
