from django.utils.translation import ugettext_lazy as _

from horizon import exceptions

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.images_and_snapshots.views import IndexView as OldIndexView

from tukey.dashboards.project.images_and_snapshots.images.tables import ImagesTable
from tukey.dashboards.project.images_and_snapshots.snapshots.tables import OtherSnapshotsTable, UserSnapshotsTable
from openstack_dashboard.dashboards.project.images_and_snapshots.volume_snapshots.tables import VolumeSnapshotsTable

# from horizon.dashboards.nova.images_and_snapshots.images.tables import ImagesTable
# from horizon.dashboards.nova.images_and_snapshots.snapshots.tables import SnapshotsTable

class IndexView(OldIndexView):
    # Wire the view to the template for modification instead of using horizon one

    table_classes = (ImagesTable, UserSnapshotsTable, OtherSnapshotsTable, VolumeSnapshotsTable)
