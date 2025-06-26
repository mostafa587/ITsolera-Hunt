import os
from urllib.parse import urlparse, parse_qs
import Payloads
import requests
import html


Current_dir = os.path.dirname(os.path.abspath(__file__)) # Get the current directory of this script
ReconnResult_path = os.path.join(Current_dir, "ReconnResult")


"""
Handles URLs by checking if they are valid and then processing them.
"""
Alive_param_urls = os.path.join(ReconnResult_path, "param_urls.txt")

if not os.path.exists(Alive_param_urls):
    print(f"[ERROR] The file {Alive_param_urls} does not exist. Please ensure it is created by the reconnaissance module.")
    exit(1)

open_alive_param_urls = open(Alive_param_urls, "r")
URL_file_contents = open_alive_param_urls.readlines() #This returns a list of the lines in the file

for url in URL_file_contents:
    url = url.strip()  # Remove any leading/trailing whitespace
    if not url:  # Skip empty lines
        continue
    parsed_url = urlparse(url).query # parsed.query → "q=test&lang=en"
    query = parse_qs(parsed_url)  # This will parse the query string into a dictionary (query → {'q': ['test'], 'lang': ['en']})

    base_url = urlparse(url).scheme + "://" + urlparse(url).netloc + urlparse(url).path + "?"
    
    

    for Payload in Payloads.payloads_encoder():
        for param, value in Payload.items():
           for param in query:
                # Copy the original query parameters
                modified_query = query.copy()
                
                # Inject the payload into one parameter
                modified_query[param] = value
                
                

                # Convert the modified query dictionary back to a query string
                query_string = param + '=' + value 
                
                # Rebuild the full URL with the injected payload
                full_url = f"{base_url}{query_string}"


                # Now it's time to send the full_url to the target server and analyze the response for XSS vulnerabilities

                print(f"[+] Testing URL: {full_url} ")
                try:
                    response = requests.get(full_url, timeout=10)
                    if value in response.text:
                        print(f"[!!!] XSS FOUND! Unsanitized payload reflected.")   
                        print(f"      URL: {full_url}\n")
                    elif html.escape(value) in response.text:
                        print(f"[~] Payload reflected, but escaped. Likely not vulnerable.")
                    else:
                        print(f"[-] Payload not reflected.")
                except Exception as e:
                    print(f"[ERROR] Request failed: {e}")

open_alive_param_urls.close()


