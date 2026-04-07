import requests
import json

login_url = 'http://127.0.0.1:5000/login'
r = requests.post(login_url, json={'uname': 'admin', 'pwd': '123'})
if r.status_code == 200:
    token = r.json().get('token')
    print('Token obtained')
    
    detect_url = 'http://127.0.0.1:5000/startDetection'
    headers = {'Authorization': token}
    payload = {
        'project_path': r'D:\AGenticVul\3s_back\results\project 8',
        'Pmodel': 'DFEVD',
        'repo_name': 'project 8',
        'pid': 'project 8'
    }
    r2 = requests.post(detect_url, json=payload, headers=headers)
    print('Status:', r2.status_code)
    print('Response:', r2.text)
else:
    print('Login failed:', r.text)
