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
    get_user_id_by_name,
    refresh_users,
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

# login
@view_config(route_name='login', renderer='templates/login.pt', permission='view')
@forbidden_view_config(renderer='templates/login.pt')
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
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        user_name = user_name,
        logged_in = request.authenticated_userid,
        )

# logout
@view_config(route_name='logout', permission='account')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_path('home'), headers = headers)

# register
@view_config(route_name='register', renderer='templates/register.pt', permission='view')
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

        user_id = get_user_id_by_name(new_user.user_name)
        refresh_users()
        headers = remember(request, user_id)
        return HTTPFound(location = request.route_path('home'), headers = headers)
    else:
        return {
                'message': '',
                'logged_in': request.authenticated_userid
                }

# account manage page
@view_config(route_name='account', renderer='templates/account.pt', permission='account')
def account(request):
    user_id = request.authenticated_userid
    user = DBSession.query(User).filter(User.id == user_id).first()
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
                        'message': 'Passwords do not match',
                        'user': user,
                        'logged_in': request.authenticated_userid
                        }
        elif password:
            return {
                    'message': 'Incorrect password',
                    'user': user,
                    'logged_in': request.authenticated_userid
                    }
        DBSession.query(User).filter(User.id == user_id).update(user_info)
        refresh_users()
        return {
                'message': 'Information updated',
                'user': user,
                'logged_in': request.authenticated_userid
                }
    return {
            'message': '',
            'user': user,
            'logged_in': request.authenticated_userid
            }

# Static

@view_config(route_name='home', renderer='templates/index.pt', permission='view')
def index(request):
    return {
            'logged_in': request.authenticated_userid,
            }

# Books

@view_config(route_name='add_book', renderer='templates/add_book.pt', permission='book')
def add_book(request):
    if request.POST:
        if hasattr(request.params['cover'], 'file'):
            import os, uuid
            input_file = request.params['cover'].file

            _here = os.path.dirname(__file__)
            file_name = '%s.jpg' % uuid.uuid4()
            # path to file from base dir
            rel_path = os.path.join('uploads', file_name)
            # full system path to file
            file_path = os.path.join(_here, rel_path)
            temp_file_path = file_path + '~'

            file_dir = os.path.dirname(file_path)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)

            output_file = open(temp_file_path, 'wb')
            input_file.seek(0)
            while True:
                data = input_file.read(2<<16)
                if not data:
                    break
                output_file.write(data)
            output_file.close()

            os.rename(temp_file_path, file_path)
        else:
            file_name = ''

        new_book = Book(
                title = request.params['title'],
                author = request.params['author'],
                cover_path = file_name
                )
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

# /book/remove/{book_id}
@view_config(route_name='remove_book', permission='book')
def remove_book(request):
    book_id = request.matchdict['book_id']
    book = DBSession.query(Book).filter(Book.id == book_id).one()
    DBSession.delete(book)

    return HTTPFound(request.route_path('view_books'))

# /book/{book_id}
@view_config(route_name='view_book', renderer='templates/view_book.pt', permission='view')
def view_book(request):
    book_id = request.matchdict['book_id']
    book = DBSession.query(Book).filter(Book.id == book_id).first()
    listings = DBSession.query(Listing).filter(Listing.book_id == book_id)
    return {
            'book': book,
            'listings': listings,
            'logged_in': request.authenticated_userid
            }

@view_config(route_name='view_books', renderer='templates/view_books.pt', permission='view')
def books(request):
    books = DBSession.query(Book)
    return {
            'books': books,
            'logged_in': request.authenticated_userid
            }

# Listings

@view_config(route_name='sell', renderer='templates/add_listing.pt', permission='sell')
def sell(request):
    if request.POST:
        new_listing = Listing(
            book_id = request.params['book_id'],
            selling_user_id = request.authenticated_userid,
            condition = request.params['condition'],
            price = request.params['price']
            )
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
