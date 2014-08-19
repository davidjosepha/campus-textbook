from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    )
from pyramid.security import (
    remember,
    forget,
    )
from .security import (
    USERS,
    get_users,
    set_password,
    check_password,
    )
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError

from .models import (
    Book,
    DBSession,
    Listing,
    User,
    )

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if request.POST:
        login = request.params['login']
        password = request.params['password']
        get_users(request)
        # if USERS.get(login) == password:
        if check_password(password, USERS.get(login)):
            headers = remember(request, login)
            return HTTPFound(location = came_from, headers = headers)
        message = 'Failed login'

    return dict (
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        logged_in = request.authenticated_userid,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'), headers = headers)

@view_config(route_name='home', renderer='templates/index.pt', permission='view')
def index(request):
    return {
            'logged_in': request.authenticated_userid,
            }

# Books

@view_config(route_name='add_book', renderer='templates/add_book.pt', permission='edit')
def add_book(request):
    if request.POST:
        new_book = Book(**request.params)
        DBSession.add(new_book)
        return {
                'message': 'You have successfully created a book',
                'logged_in': request.authenticated_userid
                }
    else:
        return {
                'message': '',
                'logged_in': request.authenticated_userid
                }

@view_config(route_name='view_book', renderer='templates/book.pt', permission='view')
def view_book(request):
    book_id = request.matchdict['book_id']
    book = DBSession.query(Book).filter(Book.id == book_id).first()
    listings = DBSession.query(Listing).filter(Listing.book_id == book_id)
    return {
            'book': book,
            'listings': listings,
            'logged_in': request.authenticated_userid
            }

@view_config(route_name='books', renderer='templates/results.pt', permission='view')
def books(request):
    books = DBSession.query(Book)
    return {
            'books': books,
            'logged_in': request.authenticated_userid
            }

# Listings

@view_config(route_name='add_listing', renderer='templates/add_listing.pt', permission='edit')
def add_listing(request):
    if request.POST:
        new_listing = Listing(**request.params)
        DBSession.add(new_listing)
        return HTTPFound(request.route_path('view_book', book_id=new_listing.book_id))
    else:
        users = DBSession.query(User)
        book_id = request.matchdict['book_id']
        book = DBSession.query(Book).filter(Book.id == book_id).first()
        return {
                'users': users,
                'book': book,
                'logged_in': request.authenticated_userid
                }

# Users

@view_config(route_name='register', renderer='templates/register.pt', permission='view')
def register(request):
    if request.POST and request.params["password"] == request.params['password_confirm']:
        user_info = {
            'user_name': request.params['user_name'],
            'password': request.params['password'],
            'first_name': request.params['first_name'],
            'last_name': request.params['last_name'],
            'graduation_year': request.params['graduation_year'],
            }
        new_user = User(**user_info)
        new_user.password = set_password(new_user.password)
        DBSession.add(new_user)
        return {
                'message': 'You have successfully created a user',
                'logged_in': request.authenticated_userid
                }
    else:
        return {
                'message': '',
                'logged_in': request.authenticated_userid
                }

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_CampusTextbook_db" scr.pt
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this scr.pt and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

