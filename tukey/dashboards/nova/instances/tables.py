from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tukey.cloud_attribute import get_cloud

from horizon import tables

from horizon.dashboards.nova.instances.tables import InstancesTable as OldInstancesTable
from horizon.dashboards.nova.instances.tables import AssociateIP as OldAssociateIP

class LaunchLink(tables.LinkAction):
    name = "launch"
    verbose_name = _("Launch Instance")
    url = "horizon:nova:images_and_snapshots:index"

class InstancesTable(OldInstancesTable):

    cloud = tables.Column(get_cloud, verbose_name=_("Cloud"))

    Meta = OldInstancesTable.Meta



class AssociateIP(OldAssociateIP):

    def allowed(self, request, instance=None):

        return get_cloud(instance) in settings.CLOUD_FUNCTIONS['associate_ip']
    
