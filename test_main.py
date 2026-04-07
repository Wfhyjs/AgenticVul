import sys
sys.path.append('d:/AGenticVul/3s_back')
from app import app
from agents import main
app.app_context().push()
try:
    main("project 8", "project 8")
except Exception as e:
    import traceback
    traceback.print_exc()
