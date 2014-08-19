from sqlalchemy.exc import DBAPIError
from .models import (
    DBSession,
    User,
    )

USERS = {}
GROUPS = {}

def get_users(request):
    users = DBSession.query(User).all()
    for user in users:
        USERS[user.user_name] = 'password'
        GROUPS[user.user_name] = ['group:users']

def groupfinder(user_id, request):
    get_users(request)
    if user_id in USERS:
        return GROUPS.get(user_id, [])
