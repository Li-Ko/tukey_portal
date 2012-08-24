

# used for all clouds by monkey-patching the cloud datatables ojects
# found in tables.py also requires modifications to html templates

# Example:
#    from tukey.cloud_attribute import get_cloud
#    table_class.cloud = tables.Column(get_cloud, verbose_name=_("Cloud"))

def get_cloud(cloud_object):
    if hasattr(cloud_object, 'cloud'):
        cloud = cloud_object.cloud
        return cloud

    elif hasattr(cloud_object, '_info'):
	if 'cloud' in cloud_object._info:
	    cloud = cloud_object._info['cloud']
	    return cloud

    elif hasattr(cloud_object._apiresource, 'cloud'):
        cloud = cloud_object._apiresource.cloud
        return cloud
    return 'Not available'
