import requests
try:
    resp = requests.get('http://localhost:8080')
    print("UI is up! Status:", resp.status_code)
except Exception as e:
    print("UI failed to start:", e)
