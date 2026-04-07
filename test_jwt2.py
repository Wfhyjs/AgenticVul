import requests
import jwt
import datetime

SECRET_KEY = "c96d8f5314ea4e72811b8cbec965d0d1eebecf5d82e0e7eaecf6b8f27c39b528"
payload = {
    'uname': 'wfyjs',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
}
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

detect_url = "http://127.0.0.1:5000/startDetection"
headers = {"Authorization": "Bearer " + token}
payload = {
    "project_path": r"D:\AGenticVul\3s_back\results\project 8",
    "Pmodel": "DFEVD",
    "repo_name": "project 8",
    "pid": 7
}
r = requests.post(detect_url, json=payload, headers=headers)
print(r.status_code)
print(r.text)
