import datetime

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Numeric, # for prices
    Text,
    DateTime,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Allow,
    Everyone,
    )

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_name = Column(Text, unique=True)
    password = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    graduation_year = Column(Integer)
    join_date = Column(DateTime, default=datetime.datetime.now)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    author = Column(Text) # Probably convert to a reference to an authors table later

class Listing(Base):
    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship("Book", backref="listing")
    selling_user_id = Column(Integer, ForeignKey('user.id'))
    selling_user = relationship("User", backref="listing")
    condition = Column(Text)
    price = Column(Numeric(None, 2))

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:users', 'edit') ]
    def __init__(self, request):
        pass
