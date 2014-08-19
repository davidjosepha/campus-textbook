from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .security import (
    group_finder,
    get_users,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # populates USERS and GROUPS
    get_users()
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=group_finder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          root_factory='.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.include('pyramid_chameleon')
    config.add_static_view('assets', 'assets', cache_max_age=3600)

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')

    config.add_route('home', '/')

    config.add_route('add_book', '/book/add')
    config.add_route('books', '/books')
    config.add_route('view_book', '/book/{book_id}')

    config.add_route('add_listing', '/book/sell/{book_id}')

    config.scan()
    return config.make_wsgi_app()
