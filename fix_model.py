import sys
files = ['agents.py', 'app.py', 'generate_report.py', 'realtime_detection.py', 'utils.py']
for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('gpt-4o-mini', 'gpt-3.5-turbo')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
