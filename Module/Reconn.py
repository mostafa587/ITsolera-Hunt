import argparse
import os
import sys
import subprocess
# Reconn.py - A reconnaissance tool that uses Sublist3r for domain enumeration



katana_path = "/home/mostafa/MAIN/TOOLS/GO/bin//katana"  # Edit this path to your katana binary location
Current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current working directory
Results_path = os.path.join(Current_dir, "ReconnResult")


def Paths(sublist3r_output_path = None, subjack_output = None):
     # Define the path for ReconnResult directory

    if not os.path.exists(Results_path): # Check if ReconnResult directory exists in user's home directory
        os.makedirs(Results_path) # Create ReconnResult directory if it doesn't exist


    if not os.path.exists(os.path.join(Results_path, "sublist3r_output.txt")) and sublist3r_output_path == True: # Check if sublist3r_output.txt exists in ReconnResult directory and sublist3r_output is True
        with open(os.path.join(Results_path, "sublist3r_output.txt"), "a") as f: # Create sublist3r_output.txt file in ReconnResult directory
            f.write("") # Write an empty string to the file to create it





def parse_args():

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Reconn - Reconnaissance Tool")
    parser.add_argument("-t", "--target", type=str, required=True, help="Domain to scan")

    parser.add_argument("-oS", "--output_sublist3r", type=str, default=os.path.join(Results_path, "sublist3r_output.txt"), help="Output file for Sublist3r results (default: sublist3r_output.txt in current directory)")

    parser.add_argument("-oJ", "--output_subjack", type=str, default=os.path.join(Results_path, "subjack_output.txt"), help="Output file for Subjack results (default: subjack_output.txt in current directory)")
    parser.add_argument("-iJ", "--input_subjack", type=str, default=os.path.join(Results_path, "sublist3r_output.txt"), help="Input file for Subjack (default: sublist3r_output.txt in current directory)")

    parser.add_argument("-oH", "--output_httpx", type=str, default=os.path.join(Results_path, "Alive_subs.txt"), help="Output file for httpx results (default: Alive_subs.txt in current directory)")
    parser.add_argument("-oK", "--output_katana", type=str, default=os.path.join(Results_path, "katana_output.txt"), help="Output file for katana results (default: katana_output.txt in current directory)")


    args =parser.parse_args()
    return args





def sublist3r():
    # Function to run Sublist3r for subdomain enumeration
    print("[+]Running Sublist3r...")

    # Initialize directory and file paths for Sublist3r output
    Paths(sublist3r_output_path = True)  
    args = parse_args()


    
    try:
        # First attempt: Try running Sublist3r directly from system PATH
        subprocess.run(["sublist3r", "-d", args.target, "-o", args.output_sublist3r], capture_output=True, check=True)
        print("[+]Sublist3r completed successfully. Output saved to:", args.output_sublist3r)


    except subprocess.CalledProcessError:
        # If direct execution fails, try to locate sublist3r.py file in system
        Results= subprocess.run(["locate", "sublist3r.py"], capture_output=True, text=True)
        sublist3r_path = Results.stdout.strip().split("\n")[0]
        print("[+]Sublist3r Path:", sublist3r_path)
        try:
            # Try running Sublist3r using the found path
            subprocess.run(["python3", sublist3r_path, "-d", args.target, "-o", args.output_sublist3r], check=True)
            print("[+]Sublist3r completed successfully. Output saved to:", args.output_sublist3r)
        except subprocess.CalledProcessError as e:
            # Handle any errors during Sublist3r execution
            print("[-]Error running Sublist3r:", e)
            sys.exit(1)


    except FileNotFoundError:
        # Handle case where Sublist3r is not installed
        print("[-]Sublist3r not found. Please install Sublist3r.")
        sys.exit(1)




def subjack(input_file=None, output_file=None):
    # Function to run Subjack for subdomain takeover detection
    print("[+]Running Subjack...")
    # Define paths for fingerprints.json file
    fingerprints_path = os.path.join(Results_path, "fingerprints.json")
    default_path = "/src/github.com/haccer/subjack/fingerprints.json"


    if os.path.exists(default_path):
        # If default fingerprints file exists, run Subjack with default configuration
        if os.path.exists(output_file):
            os.remove(output_file)
        subprocess.run(["subjack", "-w", input_file, "-o", output_file, "-t", "30", "-ssl", "-a", "-v"], check=True)
        print("[+]Subjack completed successfully. Output saved to:", output_file)



    elif os.path.exists(fingerprints_path):
        # If local fingerprints file exists, use it
        if os.path.exists(output_file):
            os.remove(output_file)
        subprocess.run(["subjack", "-w", input_file, "-o", output_file, "-t", "30", "-ssl", "-a", "-v", "-c", fingerprints_path], check=True)
        print("[+]Subjack completed successfully. Output saved to:", output_file)


    elif not os.path.exists(fingerprints_path) and not os.path.exists(default_path):
        # If no fingerprints file found, download it from GitHub
        print("[-] Local fingerprint.json also not found. Downloading...")
        try:
            # Download fingerprints.json and run Subjack
            subprocess.run(["wget", "https://raw.githubusercontent.com/haccer/subjack/master/fingerprints.json", "-O", fingerprints_path], check=True)
            print("[+] Downloaded fingerprints.json to:", fingerprints_path)
            subprocess.run(["subjack", "-w", input_file, "-o", output_file, "-t", "30", "-ssl", "-a", "-v", "-c", fingerprints_path], check=True)
            print("[+]Subjack completed successfully. Output saved to:", output_file)
        except subprocess.CalledProcessError as e:
            print("[-]Error running Subjack:", e)
            sys.exit(1)


    else:
        # Handle case where fingerprints file cannot be found or downloaded
        print("[-]Error: Unable to find fingerprints.json or default path.")
        sys.exit(1)



def httpx(input_file=None, output_file=None):
    print("[+]Running httpx...")


    try:
        subprocess.run(["httpx", "-l", input_file, "-o", output_file, "-silent", "-mc", "200,201,202,203,204,205,206,300,301,302,303,304,307,308"], check=True)

        print("[+]httpx completed successfully. Output saved to:", output_file)


    except subprocess.CalledProcessError as e:
        print("[-]Error running httpx:", e)
        sys.exit(1)


def katana(alive_hosts_path, output_file=None):
    # Function to run Katana for further analysis of alive hosts
    print("[+]Running Katana...")
    
    
    try:
            
            katana_output = os.path.join(Results_path, output_file) if output_file else os.path.join(Results_path, "katana_output.txt")
            cmd = f"{katana_path} -list {alive_hosts_path} > {katana_output}" 
            subprocess.run(cmd, shell=True,executable='/bin/zsh')
    
    
    except Exception as e:
        print("katana exception:", e)

def Alive_URLs(input_file=None):
    # Function to filter alive URLs from the output of httpx
    print("[+]Filtering alive URLs Using HTTPX...")
    input_file = os.path.join(Results_path, input_file) if input_file else os.path.join(Results_path, "Alive_subs.txt")
    output_file = os.path.join(Results_path, "alive_" + input_file.split("/")[-1])
    try:
        subprocess.run(["httpx", "-l", input_file, "-o", output_file, "-silent", "-mc", "200,201,202,203,204,205,206,300,301,302,303,304,307,308"], check=True)
        print("[+]Alive URLs filtered successfully. Output saved to:", output_file)
    except subprocess.CalledProcessError as e:
        print("[-]Error filtering alive URLs:", e)
        sys.exit(1)

def seperate_alive(input_file=None):
    # Initialize output file paths
    js_urls = os.path.join(Results_path, "js_urls.txt")
    param_urls = os.path.join(Results_path, "param_urls.txt")
    path_urls = os.path.join(Results_path, "path_urls.txt")

    # Read input file and process URLs
    with open(input_file, 'r') as f:
        urls = set(f.read().splitlines())  # Use set for automatic deduplication

    # Process and categorize URLs
    js_list = set()
    param_list = set()
    path_list = set()

    for url in urls:
        if url.endswith('.js'):
            js_list.add(url)
        elif '?' in url:
            param_list.add(url)
        else:
            path_list.add(url)

    # Write results to separate files
    if js_list:
        with open(js_urls, 'w') as f:
            f.write('\n'.join(js_list))
        print(f"[+] JavaScript URLs saved to: {js_urls}")

    if param_list:
        with open(param_urls, 'w') as f:
            f.write('\n'.join(param_list))
        print(f"[+] URLs with parameters saved to: {param_urls}")

    if path_list:
        with open(path_urls, 'w') as f:
            f.write('\n'.join(path_list))
        print(f"[+] Path URLs saved to: {path_urls}")

    
    

    
    



def main():

    args = parse_args()  # Parse command line arguments
    sublist3r()  # Call the sublist3r function to start the reconnaissance process

    subjack(args.input_subjack, args.output_subjack)  # Call the subjack function with input and output file paths

    httpx(args.output_sublist3r,args.output_httpx)  # Call the httpx function with input and output file paths

    katana(args.output_httpx, args.output_katana)  # Call the katana function with the output file from httpx For Alive Subdomains

    Alive_URLs(args.output_katana)  # Call the Alive_URLs function to filter alive URLs

    seperate_alive_input = os.path.join(Results_path, "alive_" + args.output_katana.split("/")[-1]) # The output of Alive_URLS()

    seperate_alive(seperate_alive_input) # gives you JS , parameters , DIRS 

    

main()  # Entry point of the script
    
    



