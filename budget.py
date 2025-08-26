import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db 
from app.models import User

@app.shell_context_processor
def make_shell_context(): #Registers the function as a shell context function
    return {'sa': sa, 'so': so, 'db':db, 'User':User}