"""Calls the online /predict endpoint. Usage: python scripts/test_api.py [base_url]"""
import sys
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://mpsw-getaround-api.hf.space"
response = requests.post(f"{BASE}/predict", json={
    "input": [["Citroën", 140411, 100, "diesel", "black", "convertible", True, True, False, False, True, True, True]]
})
print(response.status_code, response.json())
