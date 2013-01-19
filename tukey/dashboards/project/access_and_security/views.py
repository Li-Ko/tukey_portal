from openstack_dashboard.dashboards.project.access_and_security.views import IndexView as OldIndexView

from tukey.dashboards.project.access_and_security.keypairs.tables import KeypairsTable
from openstack_dashboard.dashboards.project.access_and_security.security_groups.tables import SecurityGroupsTable
from openstack_dashboard.dashboards.project.access_and_security.floating_ips.tables import FloatingIPsTable

class IndexView(OldIndexView):
    table_classes = (KeypairsTable, SecurityGroupsTable, FloatingIPsTable)
