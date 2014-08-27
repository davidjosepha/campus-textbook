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

from .scraper import scrape

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
@view_config(route_name='account', renderer='templates/account.pt', permission='account')
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

# Static

@view_config(route_name='home', renderer='templates/index.pt', permission='view')
def index(request):
    return {
        'page_title': 'Home',
        'logged_in': request.authenticated_userid,
        }

# Images
def save_image(request):
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
    return file_name

# Books

@view_config(route_name='add_book', renderer='templates/add_book.pt', permission='book')
def add_book(request):
    if request.POST:
        if hasattr(request.params['cover'], 'file'):
            file_name = save_image(request)
        else:
            file_name = ''

        new_book = Book(
                title = request.params['title'],
                author = request.params['author'],
                cover_path = file_name
                )
        DBSession.add(new_book)
        DBSession.commit()
        return HTTPFound(location = request.route_path('view_books'))
    else:
        return {
            'page_title': 'Add book',
            'logged_in': request.authenticated_userid,
            }

# /book/edit/{book_id}
@view_config(route_name='edit_book', renderer='templates/edit_book.pt', permission='book')
def edit_book(request):
    book_id = request.matchdict['book_id']
    book = DBSession.query(Book).filter(Book.id == book_id).one()
    if request.POST:
        book_info = {
            'title': request.params['title'],
            'author': request.params['author'],
            }
        if hasattr(request.params['cover'], 'file'):
            book_info['cover_path'] = save_image(request)

        DBSession.query(Book).filter(Book.id == book_id).update(book_info)
        DBSession.commit()
        return HTTPFound(request.route_path('view_book', book_id=book_id))
    else:
        return {
            'page_title': 'Edit book',
            'logged_in': request.authenticated_userid,
            'book': book,
            }

# /book/merge/{first_book_id}/{second_book_id}
@view_config(route_name='merge_books', renderer='templates/merge_books.pt', permission='book')
def merge_books(request):
    first_book_id = request.matchdict['first_book_id']
    first_book = DBSession.query(Book).filter(Book.id == first_book_id).one()
    second_book_id = request.matchdict['second_book_id']
    second_book = DBSession.query(Book).filter(Book.id == second_book_id).one()
    if request.POST:
        book_info = {
            'title': request.params['title'],
            'author': request.params['author'],
            }
        if 'cover_path' in request.params:
            book_info['cover_path'] = request.params['cover_path']
        DBSession.query(Book).filter(Book.id == first_book_id).update(book_info)
        DBSession.query(Listing).filter(Listing.book_id == second_book_id).update({'book_id': first_book_id})
        DBSession.delete(second_book)
        DBSession.commit()
        return HTTPFound(request.route_path('view_books'))
    else:
        return {
            'page_title': 'Merge books',
            'logged_in': request.authenticated_userid,
            'first_book': first_book,
            'second_book': second_book,
            }

# /book/remove/{book_id}
@view_config(route_name='remove_book', permission='book')
def remove_book(request):
    book_id = request.matchdict['book_id']
    book = DBSession.query(Book).filter(Book.id == book_id).one()
    DBSession.delete(book)
    DBSession.commit()

    return HTTPFound(request.route_path('view_books'))

# /book/{book_id}
@view_config(route_name='view_book', renderer='templates/view_book.pt', permission='view')
def view_book(request):
    book_id = request.matchdict['book_id']
    book = DBSession.query(Book).filter(Book.id == book_id).one()
    listings = DBSession.query(Listing).filter(Listing.book_id == book_id).order_by(Listing.price)
    return {
        'page_title': book.title,
        'logged_in': request.authenticated_userid,
        'book': book,
        }

@view_config(route_name='view_books', renderer='templates/view_books.pt', permission='view')
def books(request):
    books = DBSession.query(Book)
    return {
        'page_title': 'Books',
        'logged_in': request.authenticated_userid,
        'books': books,
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
        DBSession.commit()
        return HTTPFound(request.route_path('view_book', book_id=new_listing.book_id))
    else:
        users = DBSession.query(User)

        book_id = request.matchdict['book_id']
        book = DBSession.query(Book).filter(Book.id == book_id).one()
        return {
            'page_title': 'Sell ' + book.title,
            'logged_in': request.authenticated_userid,
            'users': users,
            'book': book,
            }

# Scraper

@view_config(route_name='scrape', permission='book')
def scrape_bookstore(request):
    scrape()
    return HTTPFound(request.route_path('home'))
