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
        USERS[user.user_name] = user.password
        GROUPS[user.user_name] = ['group:users']

def groupfinder(user_id, request):
    get_users(request)
    if user_id in USERS:
        return GROUPS.get(user_id, [])

def set_password(raw_password):
    import random
    import hashlib
    algo = 'sha1'
    #salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    #hsh = get_hexdigest(algo, salt, raw_password)
    
    salt = hashlib.sha1(str(random.random()).encode('utf-8') + str(random.random()).encode('utf-8')).hexdigest()
    hsh = hashlib.sha1(salt.encode('utf-8') + raw_password.encode('utf-8')).hexdigest()

    return '%s$%s$%s' % (algo, salt, hsh)

def check_password(raw_password, enc_password):
    import hashlib
    algo, salt, hsh = enc_password.split('$')
    #return hsh == get_hexdigest(algo, salt, raw_password)
    return hsh == hashlib.sha1(salt.encode('utf-8') + raw_password.encode('utf-8')).hexdigest()