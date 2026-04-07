import sys
path = 'd:/AGenticVul/3s_back/app.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
old = 'GitHubPath = \"https://github.com/\" + request.form.get(\'Pfilepath\')'
new = '''input_path = request.form.get('Pfilepath', '')
        if input_path.startswith('https://github.com/'):
            GitHubPath = input_path
        else:
            GitHubPath = "https://github.com/" + input_path'''
c = c.replace(old, new)
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
