from horizon.api import nova


class MultiResourceUsage(nova.Usage):



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



