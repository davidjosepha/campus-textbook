from sqlalchemy.exc import DBAPIError
from .models import (
    DBSession,
    User,
    )
from enum import IntEnum

USERS = {}
GROUPS = {}

class Group(IntEnum):
    user = 1
    janitor = 2

def get_user_id_by_name(user_name):
    user = DBSession.query(User).filter(User.user_name == user_name).first()
    if user is None:
        return None
    else:
        return user.id

# populates USERS and GROUPS with users from database
def refresh_users():
    users = DBSession.query(User).all()
    for user in users:
        USERS[user.id] = {'user_name': user.user_name, 'password': user.password}
        if user.group_id == Group.janitor:
            GROUPS[user.id] = ['group:janitors']
        else:
            GROUPS[user.id] = ['group:users']

# returns a list of groups user is in
def group_finder(user_id, request):
    if user_id in USERS:
        return GROUPS.get(user_id, [])

# creates the hashed user password field
# as salt$hash
def set_password(raw_password):
    import random, hashlib
    
    salt = hashlib.sha512(str(random.random()).encode('utf-8') + str(random.random()).encode('utf-8')).hexdigest()[:5]
    hsh = hashlib.sha512(salt.encode('utf-8') + raw_password.encode('utf-8')).hexdigest()

    return '%s$%s' % (salt, hsh)

def check_password(raw_password, enc_password):
    import hashlib
    salt, hsh = enc_password.split('$')
    return hsh == hashlib.sha512(salt.encode('utf-8') + raw_password.encode('utf-8')).hexdigest()
