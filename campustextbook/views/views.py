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

# Static

@view_config(route_name='home', renderer='campustextbook:templates/index.pt', permission='view')
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

@view_config(route_name='add_book', renderer='campustextbook:templates/add_book.pt', permission='book')
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
@view_config(route_name='edit_book', renderer='campustextbook:templates/edit_book.pt', permission='book')
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
@view_config(route_name='merge_books', renderer='campustextbook:templates/merge_books.pt', permission='book')
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
@view_config(route_name='view_book', renderer='campustextbook:templates/view_book.pt', permission='view')
def view_book(request):
    book_id = request.matchdict['book_id']
    book = DBSession.query(Book).filter(Book.id == book_id).one()
    listings = DBSession.query(Listing).filter(Listing.book_id == book_id).order_by(Listing.price)
    return {
        'page_title': book.title,
        'logged_in': request.authenticated_userid,
        'book': book,
        }

@view_config(route_name='view_books', renderer='campustextbook:templates/view_books.pt', permission='view')
def books(request):
    query = DBSession.query(Book)

    # apply filters to query
    
    # filter by department

    # filter by course

    # filter by section

    if 'p' in request.params:
        current_page = int(request.params['p'])
    else:
        current_page = 1

    results_per_page = 10
    count = query.count()
    books = query.slice(results_per_page*(current_page-1), results_per_page*current_page)

    total_pages = ((count - 1) // results_per_page) + 1
    
    if current_page > 1:
        previous_page = current_page - 1
    else:
        previous_page = None

    if current_page < total_pages:
        next_page = current_page + 1
    else:
        next_page = None

    return {
        'page_title': 'Books',
        'logged_in': request.authenticated_userid,
        'total_pages': total_pages,
        'previous_page': previous_page,
        'current_page': current_page,
        'next_page': next_page,
        'books': books,
        }

# Listings

@view_config(route_name='sell', renderer='campustextbook:templates/add_listing.pt', permission='sell')
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
