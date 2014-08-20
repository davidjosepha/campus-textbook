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

from sqlalchemy import (
    func,
    select,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    column_property,
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
    group_id = Column(Integer)
    first_name = Column(Text)
    last_name = Column(Text)
    graduation_year = Column(Integer)
    join_date = Column(DateTime, default=datetime.datetime.now)
    full_name = column_property(first_name + " " + last_name)

class Listing(Base):
    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship("Book", backref="listing")
    selling_user_id = Column(Integer, ForeignKey('user.id'))
    selling_user = relationship("User", backref="listing")
    condition = Column(Text)
    price = Column(Numeric(None, 2))

class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    author = Column(Text)
    cover_path = Column(Text)

    # I hate this, let's change it
    @property
    def image_path(self):
        if self.cover_path == '':
            return 'default.jpg'
        else:
            return self.cover_path

    low_price = column_property(select([func.min(Listing.price)]).where(Listing.book_id == id))

# initialize permissions
class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:users', ('buy', 'sell', 'account')),
                (Allow, 'group:janitors', ('buy', 'sell', 'account', 'book')) ]
    def __init__(self, request):
        pass
