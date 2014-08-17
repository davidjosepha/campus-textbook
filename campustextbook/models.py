import datetime

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Numeric, # for prices
    Text,
    DateTime,
    ForeignKey
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(Text)
    last_name = Column(Text)
    join_date = Column(DateTime, default=datetime.datetime.now)

    def format_name(self):
        return self.first_name + " " + self.last_name

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    author = Column(Text) # Probably convert to a reference to an authors table later

class Listing(Base):
    __tablename__ = 'listings'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    selling_user_id = Column(Integer, ForeignKey('users.id'))
    description = Column(Text)
    price = Column(Numeric)

    def get_book(self):
        return DBSession.query(Book).filter(Book.id == self.book_id).first()

    def get_selling_user(self):
        return DBSession.query(User).filter(User.id == self.selling_user_id).first()

    def format_price(self):
        return "$" + str(round(self.price, 2))
