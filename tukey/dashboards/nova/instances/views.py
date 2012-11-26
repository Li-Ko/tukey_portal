from django.core.urlresolvers import reverse, reverse_lazy

from horizon import api
from horizon import exceptions

from horizon.dashboards.nova.instances.views import DetailView as OldDetailView


class DetailView(OldDetailView):

    def get_data(self):
        if not hasattr(self, "_instance"):
            try:
                instance_id = self.kwargs['instance_id']
                instance = api.server_get(self.request, instance_id)
                instance.volumes = {}
                instance.full_flavor = api.flavor_get(self.request,
                                                      instance.flavor["id"])
                instance.security_groups = api.server_security_groups(
                                           self.request, instance_id)
            except:
                redirect = reverse('horizon:nova:instances:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'instance "%s".') % instance_id,
                                    redirect=redirect)
            self._instance = instance
        return self._instance

