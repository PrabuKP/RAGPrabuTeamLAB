import requests

BASE = "http://localhost:8087"

def health():
    r = requests.get(f"{BASE}/health")
    print(r.json())

if __name__ == "__main__":
    health()
