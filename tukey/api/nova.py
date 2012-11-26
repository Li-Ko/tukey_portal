from horizon.api import nova

from horizon.utils.memoized import memoized

from horizon.api.nova import server_list
from horizon.api.nova import tenant_floating_ip_list
from horizon.api.nova import tenant_quota_get
from horizon.api.nova import Quota
from horizon.api.nova import flavor_list

from tukey.cloud_attribute import get_cloud

class Usage(nova.Usage):



    """Simple wrapper around contrib/simple_usage.py."""
    _attrs = ['start', 'server_usages', 'stop', 'tenant_id',
             'total_local_gb_usage', 'total_memory_mb_usage',
             'total_vcpus_usage', 'total_hours', 'occ_y_jobs',
         'occ_y_hdfsdu', 'adler_du', 'sullivan_du',
         'sullivan_cores', 'sullivan_ram', 'adler_ram',
             'adler_cores', 'occ_lvoc_hdfsdu', 'occ_lvoc_jobs',
         'cloud_cores', 'cloud_du', 'cloud_ram', 'hadoop_jobs',
         'hadoop_hdfsdu']

    def get_summary(self):
        return {'instances': self.total_active_instances,
                'memory_mb': self.memory_mb,
                'vcpus': getattr(self, "total_vcpus_usage", 0),
                'vcpu_hours': self.vcpu_hours,
                'local_gb': self.local_gb,
                'disk_gb_hours': self.disk_gb_hours,
        'cloud_cores': getattr(self, "cloud_cores", -1),
        'cloud_du': getattr(self, "cloud_du", -1),
        'cloud_ram': getattr(self, "cloud_ram", -1),
            'hadoop_hdfsdu': getattr(self, "hadoop_hdfsdu", -1),
            'hadoop_jobs': getattr(self, "hadoop_jobs", -1),
            'occ_y_hdfsdu': getattr(self, "occ_y_hdfsdu", -1),
            'occ_y_jobs': getattr(self, "occ_y_jobs", -1),
        'adler_du': getattr(self, "adler_du", -1),
            'sullivan_du': getattr(self, "sullivan_du", -1),
            'sullivan_cores': getattr(self, "sullivan_cores", -1),
            'sullivan_ram': getattr(self, "sullivan_ram", -1),
            'adler_ram': getattr(self, "adler_ram", -1),
            'adler_cores': getattr(self, "adler_cores", -1),
            'occ_lvoc_hdfsdu': getattr(self, "occ_lvoc_hdfsdu", -1),
            'occ_lvoc_jobs': getattr(self, "occ_lvoc_jobs", -1)}


class QuotaSet2(object):
    """Wrapper for novaclient.quotas.QuotaSet objects which wraps the
    individual quotas inside Quota objects.
    """
    def __init__(self, apiresource):
        self.items = []
        for k in apiresource.keys():
            if k in ['id']:
                continue
            limit = apiresource[k]
            v = int(limit) if limit is not None else limit
            q = Quota(k, v)
            self.items.append(q)
            setattr(self, k, v)


@memoized
def tenant_quota_usages(request):
    """
    This is the new one.
    Builds a dictionary of current usage against quota for the current
    project.
    """
    if 'cloud' in request.GET:
        cloud = request.GET['cloud']
    elif 'cloud' in request.POST:
        cloud = request.POST['cloud']
    else:
        cloud = None
    by_cloud = lambda items: [item for item in items if get_cloud(item) == cloud]
    instances = by_cloud(server_list(request))
    floating_ips = by_cloud(tenant_floating_ip_list(request))
    quotas = tenant_quota_get(request, request.user.tenant_id)
    print "internal quotas", quotas
    flavors = dict([(f.id, f) for f in by_cloud(flavor_list(request))])
    volumes = []#volume_list(request)

    usages = {'instances': {'flavor_fields': [], 'used': len(instances)},
              'cores': {'flavor_fields': ['vcpus'], 'used': 0},
              'gigabytes': {'used': sum([int(v.size) for v in volumes]),
                            'flavor_fields': []},
              'volumes': {'used': len(volumes), 'flavor_fields': []},
              'ram': {'flavor_fields': ['ram'], 'used': 0},
              'floating_ips': {'flavor_fields': [], 'used': len(floating_ips)}}

    print usages

    for usage in usages:
        for instance in instances:
            for flavor_field in usages[usage]['flavor_fields']:
                usages[usage]['used'] += getattr(
                        flavors[instance.flavor['id']], flavor_field, 0)

        usages[usage]['quota'] = getattr(quotas, usage)

        if usages[usage]['quota'] is None:
            usages[usage]['quota'] = float("inf")
            usages[usage]['available'] = float("inf")
        elif type(usages[usage]['quota']) is str:
            usages[usage]['quota'] = int(usages[usage]['quota'])
        else:
            if type(usages[usage]['used']) is str:
                usages[usage]['used'] = int(usages[usage]['used'])

            usages[usage]['available'] = usages[usage]['quota'] - \
                                         usages[usage]['used']

    print usages
    return usages

