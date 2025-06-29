import requests
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, WebDriverException
from urllib.parse import urlencode

# Load payloads from file
from pathlib import Path

# Get path to the current script's directory
BASE_DIR = Path(__file__).resolve().parent

# Define your file paths relative to script location
targets_path = BASE_DIR / "Module" / "xss_targets.txt"
payloads_path = BASE_DIR / "Module" / "payloads.txt"


try:
    with open(payloads_path) as f:
        payloads = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Error: Payloads file not found.")
    exit(1)

# Set up HTTP session
session = requests.Session()
cookie_val = input("Enter session cookie (key=value, press Enter if unused): ").strip()
if cookie_val:
    try:
        key, value = cookie_val.split("=", 1)
        session.cookies.set(key.strip(), value.strip())
    except ValueError:
        print("Error: Invalid cookie format. Use key=value.")
        exit(1)

CSRF_NAMES = ['csrf', 'csrf_token', '_csrf', 'token', 'xsrf', 'xsrf_token']
GENERIC_DEFAULT = "defaultValueHere"

def extract_csrf_token(html):
    """Extract CSRF token from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    for name in CSRF_NAMES:
        # Check input fields
        tag = soup.find('input', {'name': name, 'type': ['hidden', 'text']})
        if tag and tag.get('value'):
            print(f"[+] Found CSRF token: {name} = {tag['value']}")
            return {name: tag['value']}
        # Check meta tags
        meta_tag = soup.find('meta', {'name': name})
        if meta_tag and meta_tag.get('content'):
            print(f"[+] Found CSRF token in meta: {name} = {meta_tag['content']}")
            return {name: meta_tag['content']}
    print("[!] No CSRF token found in HTML.")
    return {}

def fetch_csrf_token(url):
    """Fetch CSRF token from the given URL."""
    try:
        r = session.get(url, timeout=5)
        if r.ok:
            return extract_csrf_token(r.text)
        else:
            print(f"[!] CSRF fetch failed: Status {r.status_code} - {r.text[:500]}...")
            return {}
    except Exception as e:
        print(f"[!] CSRF fetch error: {e}")
        return {}

def test_xss_in_browser(url):
    """Test if XSS payload triggers an alert in the browser."""
    print(f"[~] Visiting render URL: {url}")
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    try:
        driver = webdriver.Chrome(service=Service(), options=opts)
    except WebDriverException as e:
        print(f"[!] Failed to initialize ChromeDriver: {e}")
        return False

    try:
        driver.set_page_load_timeout(20)
        driver.get(url)
        time.sleep(7)
        for _ in range(3):
            try:
                alert = driver.switch_to.alert
                print(f"[✅] XSS Triggered: {alert.text}")
                alert.accept()
                return True
            except NoAlertPresentException:
                time.sleep(1)
        print("[ ] No alert triggered.")
        return False
    except TimeoutException:
        print("[!] Page load timeout.")
        return False
    except Exception as e:
        print(f"[!] Browser error: {e}")
        return False
    finally:
        driver.quit()

def parse_line(raw):
    """Parse a line from the config file."""
    raw = raw.strip()
    try:
        body_type, rest = raw.split(";", 1)
        body_type = body_type.split(":")[1].strip().lower()
        parts = [p.strip() for p in rest.split(",")]
        if len(parts) < 2:
            raise ValueError("Config must include send_url and render_url.")
        send_url, render_url = parts[0], parts[1]
        fields = parts[2:]
        return body_type, send_url, render_url, fields
    except Exception as e:
        print(f"[!] Error parsing config line: {e}")
        return None, None, None, None

def run_test(body_type, send_url, render_url, fields, payload, base_data, headers_template, xss_field, csrf_url=None):
    """Run XSS test with the given payload on a single field."""
    data = base_data.copy()
    headers = headers_template.copy()

    # Inject payload into the specified xss_field and set generic default for others
    for f in fields:
        if '?' not in f:
            continue
        key = f.rstrip('!?^<>')
        if key == xss_field:
            val = data.get(key, "")
            if '<' in f:
                data[key] = payload + val
            elif '>' in f:
                data[key] = val + payload
            else:
                data[key] = payload
        else:
            data[key] = data.get(key, GENERIC_DEFAULT)

    # Fetch fresh CSRF token before each POST request if provided
    if csrf_url and any(f.startswith(tuple(CSRF_NAMES)) for f in fields):
        print(f"[~] Fetching fresh CSRF token for request...")
        csrf_data = fetch_csrf_token(csrf_url)
        if not csrf_data:
            print(f"[!] Failed to fetch CSRF token. Skipping request.")
            return False
        data.update(csrf_data)

    try:
        # Set default headers
        headers["Accept"] = "application/json, text/plain, */*"
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        # Send initial POST request
        if body_type == "json":
            headers["Content-Type"] = "application/json"
            response = session.post(send_url, headers=headers, json=data, allow_redirects=False)
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            response = session.post(send_url, headers=headers, data=data, allow_redirects=False)

        # Debug output for POST request only
        if response.request.method == "POST":
            print("\n====== Outgoing HTTP POST Request ======")
            print(f"[URL] {response.request.url}")
            print(f"[METHOD] {response.request.method}")
            print("[HEADERS]")
            for k, v in response.request.headers.items():
                print(f"{k}: {v}")
            print("[BODY]")
            body = response.request.body
            if isinstance(body, bytes):
                body = body.decode('utf-8', errors='ignore')
            print(body if body else "No body")
            print("====================================\n")

        # Handle redirects
        redirect_count = 0
        max_redirects = 5
        while response.status_code in [301, 302, 303, 307, 308] and redirect_count < max_redirects:
            redirect_url = response.headers.get("Location")
            if not redirect_url:
                print("[!] Redirect location missing.")
                return False
            if not redirect_url.startswith("http"):
                redirect_url = requests.compat.urljoin(send_url, redirect_url)
            print(f"[~] Redirected to: {redirect_url}")
            response = session.get(redirect_url, headers=headers, allow_redirects=False)
            redirect_count += 1

        print(f"[+] Final Response: {response.status_code}")
        if response.status_code >= 400:
            print(f"[!] Error Response Body: {response.text[:500]}...")

        # Consider 200, 201, or 302 as success
        if response.status_code in [200, 201, 302]:
            print(f"[+] Comment submission likely successful (Status: {response.status_code})")
            return test_xss_in_browser(render_url)
        else:
            print(f"[!] Comment submission failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"[!] Request error: {e}")
        return False

def main():
    try:
        with open(targets_path) as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        print("Error: Config file not found.")
        exit(1)

    for line in lines:
        body_type, send_url, render_url, fields = parse_line(line)
        if not send_url:
            continue

        print(f"\n[~] Testing target: {send_url} (Render: {render_url})")
        base_data = {}
        headers_template = {}
        csrf_url = None

        # Check if CSRF is needed and prompt for URL
        if any(f.startswith(tuple(CSRF_NAMES)) for f in fields):
            csrf_url = input("Enter URL to fetch CSRF token (press Enter to skip): ").strip()
            if not csrf_url:
                print("[!] CSRF token fetching skipped.")
                csrf_url = None

        # Process fields
        xss_fields = []
        for f in fields:
            key = f.rstrip('!?^<>')
            is_header = '^' in f
            needs_input = '!' in f
            is_static = '?' not in f and not needs_input

            if needs_input and not (f.startswith(tuple(CSRF_NAMES)) and csrf_url):
                val = input(f"Enter value for {key}: ")
                if is_header:
                    headers_template[key] = val
                else:
                    base_data[key] = val
            elif is_static:
                base_data[key] = ""
            if '?' in f:
                xss_fields.append(key)

        # Test each payload on one field at a time
        for payload in payloads:
            for xss_field in xss_fields:
                print(f"\n[~] Testing payload: {payload} in field: {xss_field}")
                print(f"[DEBUG] Using default '{GENERIC_DEFAULT}' for other fields: { [k for k in xss_fields if k != xss_field] }")
                success = run_test(body_type, send_url, render_url, fields, payload, base_data, headers_template, xss_field, csrf_url)
                if success:
                    print(f"[✅] XSS vulnerability confirmed with payload: {payload} in field: {xss_field}")
                    break
                else:
                    print(f"[ ] No XSS vulnerability found with payload: {payload} in field: {xss_field}")
            else:
                continue
            break

if __name__ == "__main__":
    main()