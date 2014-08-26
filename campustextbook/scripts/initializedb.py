import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Book,
    Listing,
    User,
    Department,
    Course,
    CourseSection,
    BookToSection,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def setup_course_sections_with_books(session, book_id):
    to_add = [
        Department(
            id=1,
            name='Mathematics',
            abbreviation='MATH',
        ),
        Department(
            id=2,
            name='Computer Science',
            abbreviation='CS',
        ),
        Course(
            id=1,
            department_id=1,
            course_number=236,
            name='Mathematical Structures',
        ),
        Course(
            id=2,
            department_id=2,
            course_number=241,
            name='Programming Languages',
        ),
        Course(
            id=3,
            department_id=2,
            course_number=101,
            name='Life in the age of networks',
        ),
        CourseSection(
            id=1,
            course_id=1,
            section_number=10,
            term_offered='fall',
            year_offered=2014,
            professor='Eric Egge',

        ),
        CourseSection(
            id=2,
            course_id=1,
            section_number=11,
            term_offered='fall',
            year_offered=2014,
            professor='Mark Krusemeyer',

        ),
        CourseSection(
            id=3,
            course_id=2,
            section_number=1,
            term_offered='winter',
            year_offered=2015,
            professor='DLN',

        ),
        BookToSection(
            course_section_id=2,
            book_id=book_id,
            is_required=True,
        ),
        BookToSection(
            course_section_id=3,
            book_id=book_id,
            is_required=False,
        ),
    ]

    for model in to_add:
        session.add(model)

def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = User(
                    id = 1,
                    user_name = 'user',
                    password = '4978c$ee030ddfc730a307127e0ee4ee46633602d1f0a6cb709b0a266c1d2dfe2f171552e3bf925666dd739eac18f661c35fdd07edffd7385580144c2466c5c50bbfed', # 'password'
                    group_id = 1,
                    first_name ='Test',
                    last_name = 'User',
                    graduation_year = 2016,
                    )
        DBSession.add(model)
        
        model = User(
                    id = 2,
                    user_name = 'janitor',
                    password = '4978c$ee030ddfc730a307127e0ee4ee46633602d1f0a6cb709b0a266c1d2dfe2f171552e3bf925666dd739eac18f661c35fdd07edffd7385580144c2466c5c50bbfed', # 'password'
                    group_id = 2,
                    first_name ='Test',
                    last_name = 'Janitor',
                    graduation_year = 2016,
                    )
        DBSession.add(model)

        model = Book(
                    title = 'The Unbearable Lightness of Being',
                    author = 'Milan Kundera',
                    cover_path = ''
                    )
        DBSession.add(model)

        model = Book(
                    title = 'The C Programming Language',
                    author = 'Brian W. Kernighan; Dennis M. Ritchie',
                    cover_path = ''
                    )
        DBSession.add(model)

        model = Book(
                    title = 'JavaScript: The Good Parts',
                    author = 'Douglas Crockford',
                    cover_path = ''
                    )
        DBSession.add(model)

        model = Book(
                    title = 'Learn You a Haskell for Great Good!',
                    author = 'Miran Lipovaca',
                    cover_path = ''
                    )
        DBSession.add(model)

        model = Book(
                    title = 'The Name of the Wind',
                    author = 'Patrick Rothfuss',
                    cover_path = ''
                    )
        DBSession.add(model)

        setup_course_sections_with_books(DBSession, book_id=2)

        for i in range(1,6):
            model = Listing(
                        book_id = i,
                        selling_user_id = 1,
                        condition = "Acceptable. Numerous pages bent and some portions highlighted, but still very readable.",
                        price = 6
                        )
            DBSession.add(model)

            model = Listing(
                        book_id = i,
                        selling_user_id = 2,
                        condition = "Some shelf wear.",
                        price = 13
                        )
            DBSession.add(model)
