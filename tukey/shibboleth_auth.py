import logging

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser


from openstack_auth import utils
from openstack_auth.backend import KeystoneBackend
from openstack_auth.user import set_session_from_user

from keystoneclient import exceptions as keystone_exceptions
from openstack_auth.exceptions import KeystoneAuthException


from django.contrib.auth.signals import user_logged_in


LOG = logging.getLogger(__name__)

def get_user(request):
    try:
	LOG.debug("in get user new")
        user_id = request.session[auth.SESSION_KEY]
        backend_path = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_path)
        backend.request = request
	LOG.debug("about to call backend.get_user")
	LOG.debug(backend)
        user = backend.get_user(user_id) or AnonymousUser()
	LOG.debug("user %s", user)
    except KeyError:
        if 'HTTP_EPPN' in request.META and request.META.get('HTTP_EPPN'):
            LOG.debug("Shibboleth header is set")
            LOG.debug("username %s", request.META.get('HTTP_EPPN'))

            keystone = KeystoneBackend()
            try:
                user = keystone.authenticate(password='shibboleth',
                    username=request.META.get('HTTP_EPPN'),
                    auth_url=settings.OPENSTACK_KEYSTONE_URL,
                    request=request)
                return user
            except keystone_exceptions.Unauthorized:
                msg = _('Invalid user name or password.')
            except KeystoneAuthException:
                pass
        user = AnonymousUser()
    return user


def login(request, user):
    LOG.debug("in login")
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    if auth.SESSION_KEY in request.session:
        if request.session[auth.SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[auth.SESSION_KEY] = user.id
    request.session[auth.BACKEND_SESSION_KEY] = user.backend
    
    set_session_from_user(request, user)

    if hasattr(request, 'user'):
        request.user = user
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    LOG.debug("made it to the end")


def patch_openstack_middleware_get_user():

    LOG.debug(auth.login)

    auth.login = login

    LOG.debug(auth.login)

    utils.get_user = get_user
    
    from django_openid_auth import auth as django_openid_auth
    from tukey.openid_auth import OpenIDBackend as new_openid
    django_openid_auth.OpenIDBackend = new_openid
    
    from django_openid_auth import views as openid_views
    from tukey.openid_auth import login_begin as new_login_begin
    openid_views.login_begin = new_login_begin
