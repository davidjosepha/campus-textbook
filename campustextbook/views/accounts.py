import transaction
from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    )
from pyramid.security import (
    remember,
    forget,
    )
from ..security import (
    USERS,
    get_user_id_by_name,
    refresh_users,
    set_password,
    check_password,
    )
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError

from ..models import (
    Book,
    DBSession,
    Listing,
    User,
    )

from ..scraper import scrape

# login
@view_config(route_name='login', renderer='campustextbook:templates/login.pt', permission='view')
@forbidden_view_config(renderer='campustextbook:templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = request.route_path('home')
    came_from = request.params.get('came_from', referrer)
    message = ''
    user_name = ''
    if request.POST:
        user_name = request.params['user_name']
        user_id = get_user_id_by_name(user_name)
        password = request.params['password']
        if user_id and check_password(password, USERS.get(user_id)['password']):
            headers = remember(request, user_id)
            return HTTPFound(location = came_from, headers = headers)
        message = 'Failed login'

    return dict (
        page_title = 'Login',
        logged_in = request.authenticated_userid,
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        user_name = user_name,
        )

# logout
@view_config(route_name='logout', permission='account')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_path('home'), headers = headers)

# register
@view_config(route_name='register', renderer='campustextbook:templates/register.pt', permission='view')
def register(request):
    if request.POST and request.params['password'] == request.params['password_confirm']:
        if request.params['password'] != request.params['password_confirm']:
            return {
                    'message': 'Passwords do not match',
                    'logged_in': request.pathenticated_userid
                    }

        new_user = User(
            user_name = request.params['user_name'],
            password = set_password(request.params['password']),
            first_name = request.params['first_name'],
            last_name = request.params['last_name'],
            graduation_year = request.params['graduation_year']
            )
        DBSession.add(new_user)
        DBSession.commit()

        # I think this can be replaced by user_id = new_user.id
        # since we switched to manual commits
        user_id = get_user_id_by_name(new_user.user_name)
        refresh_users()
        headers = remember(request, user_id)
        return HTTPFound(location = request.route_path('home'), headers = headers)
    else:
        return {
            'page_title': 'Register',
            'logged_in': request.authenticated_userid,
            'message': '',
            }

# account manage page
@view_config(route_name='account', renderer='campustextbook:templates/account.pt', permission='account')
def account(request):
    user_id = request.authenticated_userid
    user = DBSession.query(User).filter(User.id == user_id).one()
    if request.POST:
        user_info = {
            'first_name': request.params['first_name'],
            'last_name': request.params['last_name'],
            'graduation_year': request.params['graduation_year'],
            }
        password = request.params['old_password']

        if check_password(password, USERS.get(user_id)['password']):
            if request.params['new_password'] == request.params['new_password_confirm']:
                user_info['password'] = set_password(request.params['new_password'])
            else:
                return {
                    'page_title': 'Manage account',
                    'logged_in': request.authenticated_userid,
                    'message': 'Passwords do not match',
                    'user': user,
                    }
        elif password:
            return {
                'page_title': 'Manage account',
                'logged_in': request.authenticated_userid,
                'message': 'Incorrect password',
                'user': user,
                }
        DBSession.query(User).filter(User.id == user_id).update(user_info)
        DBSession.commit()
        refresh_users()
        return {
            'page_title': 'Manage account',
            'logged_in': request.authenticated_userid,
            'message': 'Information updated',
            'user': user,
            }
    return {
        'page_title': 'Manage account',
        'logged_in': request.authenticated_userid,
        'message': '',
        'user': user,
        }
