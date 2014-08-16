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
