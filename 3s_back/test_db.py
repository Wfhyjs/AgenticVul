from app import app, db
from models import User
app.app_context().push()
users = User.query.all()
for u in users:
    print(u.Uname, u.Upassword)
