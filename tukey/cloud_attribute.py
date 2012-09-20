

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

# will require some sort of context for querying an api or reading
# a config file to see what the names are of the clouds
# For now it is a stub 
def cloud_names():
    return ["adler", "sullivan"]

def cloud_details():
    return {
	'adler': 'Adler, a Eucalyptus based utility cloud.',
	'sullivan': 'Sullivan, an OpenStack based utility cloud.'
    }

def has_function(function, cloud):
    functions = {
	"import_keypair": "sullivan"
    }
    if function in functions:
        return cloud in functions[function]
    return True
