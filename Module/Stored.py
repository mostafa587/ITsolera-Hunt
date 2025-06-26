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
try:
    with open("/home/slom/Programs/tools/ITsolera-Hunt/Module/payloads.txt") as f:
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
        driver.set_page_load_timeout(15)
        driver.get(url)
        # Wait longer for scripts to execute
        time.sleep(5)
        for _ in range(3):  # Retry alert detection
            try:
                alert = driver.switch_to.alert
                print(f"[✅] XSS Triggered: {alert.text}")
                alert.accept()
                return True
            except NoAlertPresentException:
                time.sleep(1)  # Wait before retrying
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

def run_test(body_type, send_url, render_url, fields, payload, base_data, headers_template, skip_csrf=False):
    """Run XSS test with the given payload."""
    data = base_data.copy()
    headers = headers_template.copy()

    # Inject payload into fields marked with '?'
    xss_fields = []
    for f in fields:
        if '?' not in f:
            continue
        key = f.rstrip('!?^<>')
        val = data.get(key, "")
        if '<' in f:
            data[key] = payload + val
        elif '>' in f:
            data[key] = val + payload
        else:
            data[key] = payload
        xss_fields.append(key)

    # Update CSRF token if not skipped
    if not skip_csrf and any(f.startswith(tuple(CSRF_NAMES)) for f in fields):
        data.update(fetch_csrf_token(send_url))

    try:
        # Set default headers
        headers["Accept"] = "application/json, text/plain, */*"
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        # Send request
        if body_type == "json":
            headers["Content-Type"] = "application/json"
            response = session.post(send_url, headers=headers, json=data, allow_redirects=False)
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            response = session.post(send_url, headers=headers, data=data, allow_redirects=False)

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
            # Use GET for 303 redirects, POST for others
            if response.status_code == 303:
                response = session.get(redirect_url, headers=headers, allow_redirects=False)
            else:
                if body_type == "json":
                    response = session.post(redirect_url, headers=headers, json=data, allow_redirects=False)
                else:
                    response = session.post(redirect_url, headers=headers, data=data, allow_redirects=False)
            redirect_count += 1

        # Debug output
        print("\n====== Outgoing HTTP Request ======")
        print(f"[URL] {response.request.url}")
        print(f"[METHOD] {response.request.method}")
        print("[HEADERS]")
        for k, v in response.request.headers.items():
            print(f"{k}: {v}")
        print("[BODY]")
        body = response.request.body.decode('utf-8') if isinstance(response.request.body, bytes) else response.request.body
        print(body if body else "No body")
        print("===================================\n")
        print(f"[+] Final Response: {response.status_code}")
        if response.status_code >= 400:
            print(f"[!] Error Response Body: {response.text[:500]}...")

        # Check for success (200 or 201)
        if response.status_code in [200, 201]:
            print(f"[+] Comment submission successful (Status: {response.status_code})")
            # Test for XSS in browser
            return test_xss_in_browser(render_url)
        else:
            print(f"[!] Comment submission failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"[!] Request error: {e}")
        return False

def main():
    try:
        with open("/home/slom/Programs/tools/ITsolera-Hunt/Module/xss_targets.txt") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        print("Error: Config file not found.")
        exit(1)

    skip_csrf = input("Skip CSRF token fetching? (y/n): ").strip().lower() == 'y'

    for line in lines:
        body_type, send_url, render_url, fields = parse_line(line)
        if not send_url:
            continue

        print(f"\n[~] Testing target: {send_url} (Render: {render_url})")
        base_data = {}
        headers_template = {}

        # Process fields
        for f in fields:
            key = f.rstrip('!?^<>')
            is_header = '^' in f
            needs_input = '!' in f
            is_static = '?' not in f and not needs_input

            if needs_input:
                val = input(f"Enter value for {key}: ")
                if is_header:
                    headers_template[key] = val
                else:
                    base_data[key] = val
            elif is_static:
                base_data[key] = ""

        # Test each payload
        for payload in payloads:
            print(f"\n[~] Testing payload: {payload}")
            success = run_test(body_type, send_url, render_url, fields, payload, base_data, headers_template, skip_csrf)
            if success:
                print(f"[✅] XSS vulnerability confirmed with payload: {payload}")
            else:
                print(f"[ ] No XSS vulnerability found with payload: {payload}")

if __name__ == "__main__":
    main()