from sqlalchemy.exc import DBAPIError
from .models import (
    DBSession,
    User,
    )

USERS = {}
GROUPS = {}

def get_user_id_by_name(user_name):
    user = DBSession.query(User).filter(User.user_name == user_name).first()
    if user is None:
        return None
    else:
        return user.id

# populates USERS with users from database
def get_users(request):
    users = DBSession.query(User).all()
    for user in users:
        USERS[user.id] = {'user_name': user.user_name, 'password': user.password}
        GROUPS[user.id] = ['group:users']

# returns a list of groups user is in
def groupfinder(user_id, request):
    get_users(request)
    if user_id in USERS:
        return GROUPS.get(user_id, [])

# creates the hashed user password field
# as salt$hash
def set_password(raw_password):
    import random
    import hashlib
    
    salt = hashlib.sha1(str(random.random()).encode('utf-8') + str(random.random()).encode('utf-8')).hexdigest()
    hsh = hashlib.sha1(salt.encode('utf-8') + raw_password.encode('utf-8')).hexdigest()

    return '%s$%s' % (salt, hsh)

def check_password(raw_password, enc_password):
    import hashlib
    salt, hsh = enc_password.split('$')
    return hsh == hashlib.sha1(salt.encode('utf-8') + raw_password.encode('utf-8')).hexdigest()
