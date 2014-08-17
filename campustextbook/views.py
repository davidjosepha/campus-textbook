from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    Book,
    DBSession,
    Listing,
    User,
    )


@view_config(route_name='users', renderer='templates/users.pt')
def list_users(request):
    users = DBSession.query(User)
    return {'message': '', 'users': users}

@view_config(route_name='users', renderer='templates/users.pt', request_method='POST')
def create_user(request):
    new_user = User(**request.params)
    DBSession.add(new_user)
    users = DBSession.query(User)
    return {'message': 'You have successfully created a user', 'users': users}

@view_config(route_name='books', renderer='templates/books.pt')
def list_books(request):
    books = DBSession.query(Book)
    return {'message': '', 'books': books}

@view_config(route_name='books', renderer='templates/books.pt', request_method='POST')
def create_book(request):
    new_book = Book(**request.params)
    DBSession.add(new_book)
    books = DBSession.query(Book)
    return {'message': 'You have successfully created a book', 'books': books}

@view_config(route_name='listings', renderer='templates/listings.pt')
def list_listings(request):
    listings = DBSession.query(Listing)
    users = DBSession.query(User)
    books = DBSession.query(Book)
    return {'message': '', 'listings': listings, 'users': users, 'books': books}

@view_config(route_name='listings', renderer='templates/listings.pt', request_method='POST')
def create_listing(request):
    new_listing = Listing(**request.params)
    DBSession.add(new_listing)
    listings = DBSession.query(Listing)
    users = DBSession.query(User)
    books = DBSession.query(Book)
    return {'message': 'You have successfully created a listing', 'listings': listings, 'users': users, 'books': books}

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_CampusTextbook_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

