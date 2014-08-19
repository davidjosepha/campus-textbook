from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError

from .models import (
    Book,
    DBSession,
    Listing,
    User,
    )


@view_config(route_name='home', renderer='templates/index.pt')
def index(request):
    return {}

# Books

@view_config(route_name='add_book', renderer='templates/add_book.pt')
def add_book(request):
    if request.POST:
        new_book = Book(**request.params)
        DBSession.add(new_book)
        return {'message': 'You have successfully created a book'}
    else:
        return {'message': ''}

@view_config(route_name='view_book', renderer='templates/book.pt')
def view_book(request):
    book_id = request.matchdict['book_id']
    book = DBSession.query(Book).filter(Book.id == book_id).first()
    listings = DBSession.query(Listing).filter(Listing.book_id == book_id)
    return {'book': book, 'listings': listings}

@view_config(route_name='books', renderer='templates/results.pt')
def books(request):
    books = DBSession.query(Book)
    return {'books': books}

# Listings

@view_config(route_name='add_listing', renderer='templates/add_listing.pt')
def add_listing(request):
    if request.POST:
        new_listing = Listing(**request.params)
        DBSession.add(new_listing)
        return HTTPFound(request.route_path('view_book', book_id=new_listing.book_id))
    else:
        users = DBSession.query(User)
        book_id = request.matchdict['book_id']
        book = DBSession.query(Book).filter(Book.id == book_id).first()
        return {'users': users, 'book': book}

# Users

@view_config(route_name='register', renderer='templates/register.pt')
def register(request):
    if request.POST:
        new_user = User(**request.params)
        DBSession.add(new_user)
        return {'message': 'You have successfully created a user'}
    else:
        return {'message': ''}

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

