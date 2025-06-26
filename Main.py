import sys
import subprocess
import os

def main():
    args = sys.argv[1:]

    if not args:
        # If no valid arguments matched, show possible arguments
        print("Invalid arguments.")
        print("Possible arguments:")
        print("  --xssReflected")
        print("  --sqli")
        print("  --cmd [--encode] [--copy] [--export]")
        return

    # Handle --xssReflected
    if "--xssReflected" in args:
        param_urls_path = os.path.join("Module", "ReconnResult", "param_urls.txt")
        if os.path.isfile(param_urls_path):
            reflected_path = os.path.join("Module", "Reflected.py")
            subprocess.run(["python3", reflected_path])
        else:
            print(f"{param_urls_path} not found.")
        return
    if "--StoredXSS" in args:
        StoredXSS = os.path.join("Module", "Stored.py")
        subprocess.run(["python3", StoredXSS])
        return
    # Handle --sqli
    if "--sqli" in args:
        sqli_path = os.path.join("Module", "sqli_generator.py")
        subprocess.run(["python3", sqli_path])
        return

    # Handle CMDi.py with multiple arguments
    cmdi_valid_args = {"--cmd", "--encode", "--copy", "--export"}
    if any(arg in cmdi_valid_args for arg in args):
        cmdi_path = os.path.join("CMDi", "CMDi.py")
        subprocess.run(["python3", cmdi_path] + args)
        return

    

if __name__ == "__main__":
    main()
