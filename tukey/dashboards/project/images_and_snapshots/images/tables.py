from django.conf import settings
from tukey.cloud_attribute import get_cloud

from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard.dashboards.project.images_and_snapshots.images.tables import (
    ImagesTable as OldImagesTable,
    LaunchImage as OldLaunchImage)

from openstack_dashboard.dashboards.project.images_and_snapshots.images.tables import EditImage, UpdateRow, CreateImage, DeleteImage

from tukey.cloud_attribute import get_cloud


class LaunchImage(OldLaunchImage):

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({"source_type": "image_id",
                "cloud": get_cloud(datum),
                            "source_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])

class LaunchCluster(tables.LinkAction):
    name = "launch_cluster"
    verbose_name = _("Launch Cluster")
    url = "horizon:project:instances:launch_cluster"
    classes = ("btn-launch", "ajax-modal")

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({"source_type": "image_id",
                "cloud": get_cloud(datum),
                            "source_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])

    def allowed(self, request, image):
        return get_cloud(image).lower() in settings.CLOUD_FUNCTIONS['launch_cluster']

class ImageFilterAction(tables.FilterAction):

    def filter(self, table, instances, filter_string):
        q = filter_string.lower()
        return [instance for instance in instances if q in instance.name.lower()]

class ImagesTable(OldImagesTable):
    cloud = tables.Column(get_cloud, verbose_name=_("Cloud"))

    class Meta:
        name = "images"
        row_class = UpdateRow
        status_columns = ["status"]
        verbose_name = _("Images")
        table_actions = (CreateImage, DeleteImage, ImageFilterAction)
        row_actions = (LaunchImage, LaunchCluster, EditImage, DeleteImage,)
        pagination_param = "image_marker"
