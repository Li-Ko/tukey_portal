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

from django import shortcuts

#TODO double check these
import functools

from django.utils.decorators import available_attrs
from django.utils.translation import ugettext as _

from horizon.exceptions import NotAuthorized, NotAuthenticated
# end double check

from horizon import decorators

from .models import UnregisteredUser

LOG = logging.getLogger(__name__)

def get_user(request):
    try:
        user_id = request.session[auth.SESSION_KEY]
        backend_path = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_path)
        backend.request = request
        user = backend.get_user(user_id) or AnonymousUser()
	LOG.debug("user %s", user)
    except KeyError:
        shib_header = None
	for possible_header in settings.SHIB_HEADERS:
            if possible_header in request.META and request.META.get(
                possible_header):
                shib_header = possible_header
                break

        if shib_header is not None:
            
            LOG.debug("Shibboleth header is set")
            LOG.debug("username %s", request.META.get(shib_header))

            keystone = KeystoneBackend()
            try:
                user = keystone.authenticate(password='shibboleth',
                    username=request.META.get(shib_header),
                    auth_url=settings.OPENSTACK_KEYSTONE_URL,
                    request=request)
                return user
            except (keystone_exceptions.Unauthorized, KeystoneAuthException):
		user = UnregisteredUser('Shibboleth', 
		    request.META.get(shib_header))

	else:
            user = AnonymousUser()
    return user


def login(request, user):
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


# monkey-patching this does nothing probably because the 
# decorators are applied before our monkey patch function
# is called.  imperitave we find a way around this.

#def require_auth(view_func):
#    """ Performs user authentication check.
#
#    Similar to Django's `login_required` decorator, except that this throws
#    :exc:`~horizon.exceptions.NotAuthenticated` exception if the user is not
#    signed-in.
#    """
#
#    @functools.wraps(view_func, assigned=available_attrs(view_func))
#    def dec(request, *args, **kwargs):
#        if request.user.is_authenticated():
#            return view_func(request, *args, **kwargs)
#	return None
#        raise NotAuthenticated(_("Please log in to continue."))
#    return dec



def patch_openstack_middleware_get_user():

    LOG.debug(auth.login)

    auth.login = login

    LOG.debug(auth.login)


#TODO: make this actually work instead of altering the
# horizon source.
#    from horizon import decorators as horizon_decorators
#    LOG.debug(horizon_decorators.require_auth)
#    horizon_decorators.require_auth = require_auth
#    LOG.debug(horizon_decorators.require_auth)


    utils.get_user = get_user
    
    from django_openid_auth import auth as django_openid_auth
    from tukey.openid_auth import OpenIDKeystoneBackend
    django_openid_auth.OpenIDBackend = OpenIDKeystoneBackend
#    OpenIDKeystoneBackend.backendclass = django_openid_auth.OpenIDBackend
    
    from django_openid_auth import views as openid_views
    from tukey.openid_auth import login_begin as new_login_begin
    openid_views.login_begin = new_login_begin

    from tukey.openid_auth import login_complete as new_login_complete
    openid_views.login_complete = new_login_complete


    from horizon.usage import base
    base.GlobalUsage.show_terminated = True

    base.TenantUsage.attrs = ('memory_mb', 'vcpus', 'uptime',
             'hours', 'local_gb', 'adler_ram')

    from create_patches import test_run
    test_run()
