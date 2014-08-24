import datetime

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    DateTime,
    Enum,
    Boolean,
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

    listings = relationship("Listing", cascade="delete")

class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    abbreviation = Column(String(length=4), unique=True)
    courses = relationship('Course', backref='department', cascade="delete")

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('department.id'))
    course_number = Column(Integer)
    name = Column(Text)

class CourseSection(Base):
    __tablename__ = 'course_section'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'))
    section_number = Column(Integer)
    term_offered = Column(Enum('fall', 'winter', 'spring', name='class_terms'))
    year_offered = Column(Integer)
    professor = Column(Text)

    course = relationship('Course', backref='section')
    book_associations = relationship('BookToSection', backref='course_section')

class BookToSection(Base):
    __tablename__ = 'book_to_section'
    course_section_id = Column(Integer, ForeignKey('course_section.id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    is_required = Column(Boolean)

    book = relationship('Book', backref='section_association')

class Listing(Base):
    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    selling_user_id = Column(Integer, ForeignKey('user.id'))
    condition = Column(Text)
    price = Column(Integer)

    book = relationship('Book', backref='listing')
    selling_user = relationship('User', backref='listing')

class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    author = Column(Text)
    cover_path = Column(Text)
    isbn = Column(String(length=13))
    edition = Column(Text)
    published_year = Column(Integer)
    publisher = Column(Text)

    listings = relationship("Listing", cascade="delete")
    low_price = column_property(select([func.min(Listing.price)]).where(Listing.book_id == id))

# initialize permissions
class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:users', ('buy', 'sell', 'account')),
                (Allow, 'group:janitors', ('buy', 'sell', 'account', 'book')) ]
    def __init__(self, request):
        pass
