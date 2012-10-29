

# used for all clouds by monkey-patching the cloud datatables ojects
# found in tables.py also requires modifications to html templates

# Example:
#    from tukey.cloud_attribute import get_cloud
#    table_class.cloud = tables.Column(get_cloud, verbose_name=_("Cloud"))

#TODO: transition to a cloudname and cloud if tags
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


def get_cloud_id(cloud_object):
    if hasattr(cloud_object, 'cloud_id'):
        cloud = cloud_object.cloud
        return cloud

    elif hasattr(cloud_object, '_info'):
	if 'cloud_id' in cloud_object._info:
	    cloud = cloud_object._info['cloud_id']
	    return cloud

    elif hasattr(cloud_object._apiresource, 'cloud_id'):
        cloud = cloud_object._apiresource.cloud_id
        return cloud
    return 'Not available'



# will require some sort of context for querying an api or reading
# a config file to see what the names are of the clouds
# For now it is a stub 
def cloud_names():
    return ["adler", "sullivan"]

def cloud_details():
    return {
	'adler': 'Adler instances.',
	'sullivan': 'Sullivan instances.'
    }

def has_function(function, cloud):
    # easier just to keep track that Adler Euca <= 2 has no import
    functions = {
	"import_keypair": "adler"
    }
    if function in functions:
        return cloud not in functions[function]
    return True
