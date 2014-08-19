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
    get_user_id_by_name,
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

# login page
# redirects to previous page after logging in
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
    if request.POST:
        login = request.params['login']
        user_id = get_user_id_by_name(login)
        password = request.params['password']
        get_users(request)
        if user_id and check_password(password, USERS.get(user_id)['password']):
            headers = remember(request, user_id)
            return HTTPFound(location = came_from, headers = headers)
        message = 'Failed login'

    return dict (
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        logged_in = request.authenticated_userid,
        )

# logout page
@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'), headers = headers)

# register page
@view_config(route_name='register', renderer='templates/register.pt', permission='view')
def register(request):
    if request.POST and request.params['password'] == request.params['password_confirm']:
        # I don't like this
        # If **request.params is passed, there's
        # an error about 'password_confirm' being
        # included, so I just made a new dictionary
        # like this. But there should be a better way
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

# Static

# index page
@view_config(route_name='home', renderer='templates/index.pt', permission='view')
def index(request):
    return {
            'logged_in': request.authenticated_userid,
            }

# Books

# add book page
# allows user to add a new book to the database
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

# view book page
# gets book_id from url (/book/{book_id})
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

# results page
# shows list of books (based on a query)
@view_config(route_name='books', renderer='templates/results.pt', permission='view')
def books(request):
    books = DBSession.query(Book)
    return {
            'books': books,
            'logged_in': request.authenticated_userid
            }

# Listings

# add listing page
# allows user to add a new listing of a book to the database
@view_config(route_name='add_listing', renderer='templates/add_listing.pt', permission='edit')
def add_listing(request):
    if request.POST:
        listing_info = {
            'book_id': request.params['book_id'],
            'selling_user_id': request.authenticated_userid,
            'condition': request.params['condition'],
            'price': request.params['price'],
            }
        new_listing = Listing(**listing_info)
        DBSession.add(new_listing)
        return HTTPFound(request.route_path('view_book', book_id=new_listing.book_id))
    else:
        users = DBSession.query(User)
        book_id = request.matchdict['book_id']
        book = DBSession.query(Book).filter(Book.id == book_id).first()
        return {
                'users': users,
                'book': book,
                'logged_in': request.authenticated_userid,
                }

# Users

