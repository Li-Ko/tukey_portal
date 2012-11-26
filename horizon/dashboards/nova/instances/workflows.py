# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.utils.text import normalize_newlines
from django.utils.translation import ugettext as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import workflows
from horizon.openstack.common import jsonutils

from tukey.cloud_attribute import get_cloud


class SelectProjectUserAction(workflows.Action):
    project_id = forms.ChoiceField(label=_("Project"))
    user_id = forms.ChoiceField(label=_("User"))

    def __init__(self, request, *args, **kwargs):
        super(SelectProjectUserAction, self).__init__(request, *args, **kwargs)
        # Set our project choices
        projects = [(tenant.id, tenant.name)
                    for tenant in request.user.authorized_tenants]
        self.fields['project_id'].choices = projects

        # Set our user options
        users = [(request.user.id, request.user.username)]
        self.fields['user_id'].choices = users


    class Meta:
        name = _("Project & User")
        permissions = ("openstack.roles.admin",)
        help_text = _("Admin users may optionally select the project and "
                      "user for whom the instance should be created.")


class SelectProjectUser(workflows.Step):
    action_class = SelectProjectUserAction
    contributes = ("project_id", "user_id")



class SetInstanceDetailsAction(workflows.Action):
    SOURCE_TYPE_CHOICES = (
        ("image_id", _("Image")),
        ("instance_snapshot_id", _("Snapshot")),
    )
    source_type = forms.ChoiceField(label=_("Instance Source"),
                                    choices=SOURCE_TYPE_CHOICES)
    image_id = forms.ChoiceField(label=_("Image"), required=False)
    instance_snapshot_id = forms.ChoiceField(label=_("Instance Snapshot"),
                                             required=False)
    name = forms.CharField(max_length=80, label=_("Server Name"))
    flavor = forms.ChoiceField(label=_("Flavor"),
                               help_text=_("Size of image to launch."))
    count = forms.IntegerField(label=_("Instance Count"),
                               min_value=1,
                               initial=1,
                               help_text=_("Number of instances to launch."))
    cloud = forms.CharField(max_length=80, label=_("Cloud Name"))
    
    #count.widget.attrs['readonly'] = True
    
    cloud.widget.attrs['readonly'] = True

    class Meta:
        name = _("Details")
        help_text_template = ("nova/instances/"
                              "_launch_details_help.html")

    def clean(self):
        cleaned_data = super(SetInstanceDetailsAction, self).clean()

        # Validate our instance source.
        source = cleaned_data['source_type']
        # There should always be at least one image_id choice, telling the user
        # that there are "No Images Available" so we check for 2 here...
        if source == 'image_id' and not \
                filter(lambda x: x[0] != '', self.fields['image_id'].choices):
            raise forms.ValidationError(_("There are no image sources "
                                          "available; you must first create "
                                          "an image before attempting to "
                                          "launch an instance."))
        if not cleaned_data[source]:
            raise forms.ValidationError(_("Please select an option for the "
                                          "instance source."))

        # Prevent launching multiple instances with the same volume.
        # TODO(gabriel): is it safe to launch multiple instances with
        # a snapshot since it should be cloned to new volumes?
        count = cleaned_data.get('count', 1)
        volume_type = self.data.get('volume_type', None)
        if volume_type and count > 1:
            msg = _('Launching multiple instances is only supported for '
                    'images and instance snapshots.')
            raise forms.ValidationError(msg)

        return cleaned_data

    def _get_available_images(self, request, context):
        project_id = context.get('project_id', None)
        if not hasattr(self, "_public_images"):
            public = {"is_public": True}
            try:
                public_images, _more = api.glance.image_list_detailed(request,
                                                           filters=public)
            except:
                public_images = []
                exceptions.handle(request,
                                  _("Unable to retrieve public images."))
            self._public_images = public_images

        # Preempt if we don't have a project_id yet.
        if project_id is None:
            setattr(self, "_images_for_%s" % project_id, [])

        if not hasattr(self, "_images_for_%s" % project_id):
            owner = {"property-owner_id": project_id}
            try:
                owned_images, _more = api.glance.image_list_detailed(request,
                                                          filters=owner)
            except:
                exceptions.handle(request,
                                  _("Unable to retrieve images for "
                                    "the current project."))
            setattr(self, "_images_for_%s" % project_id, owned_images)

        owned_images = getattr(self, "_images_for_%s" % project_id)
        images = owned_images + self._public_images

        # Remove duplicate images.
        image_ids = []
        final_images = []
        for image in images:
            if image.id not in image_ids:
                image_ids.append(image.id)
                final_images.append(image)
        return [image for image in final_images
                if image.container_format not in ('aki', 'ari')]

    def populate_image_id_choices(self, request, context):
        images = self._get_available_images(request, context)

	if 'cloud' in request.GET:
	    cloud = request.GET['cloud']
            choices = [(image.id, image.name)
                   for image in images
                   if image.properties.get("image_type", '') != "snapshot"
		    and (get_cloud(image) == cloud)]
	else:
            choices = [(image.id, image.name)
                   for image in images
                   if image.properties.get("image_type", '') != "snapshot"]
        if choices:
            choices.insert(0, ("", _("Select Image")))
        else:
            choices.insert(0, ("", _("No images available.")))
        return choices

    def populate_instance_snapshot_id_choices(self, request, context):
        images = self._get_available_images(request, context)
        choices = [(image.id, image.name)
                   for image in images
                   if image.properties.get("image_type", '') == "snapshot"]
        if choices:
            choices.insert(0, ("", _("Select Instance Snapshot")))
        else:
            choices.insert(0, ("", _("No snapshots available.")))
        return choices

    def populate_flavor_choices(self, request, context):
        try:
            flavors = api.nova.flavor_list(request)

            if 'cloud' in request.GET:
                cloud = request.GET['cloud']
                flavor_list = [(flavor.id, "%s" % flavor.name)
                           for flavor in flavors
			   if get_cloud(flavor) == cloud]
	    else:
                flavor_list = [(flavor.id, "%s" % flavor.name)
                           for flavor in flavors]
        except:
            flavor_list = []
            exceptions.handle(request,
                              _('Unable to retrieve instance flavors.'))
        return sorted(flavor_list)

    def get_help_text(self):
        extra = {}
        try:
            extra['usages'] = api.nova.tenant_quota_usages(self.request)
            extra['usages_json'] = jsonutils.dumps(extra['usages'])
            flavors = jsonutils.dumps([f._info for f in
                                       api.nova.flavor_list(self.request)])
            extra['flavors'] = flavors
        except:
            exceptions.handle(self.request,
                              _("Unable to retrieve quota information."))
        return super(SetInstanceDetailsAction, self).get_help_text(extra)




class SetInstanceDetails(workflows.Step):
    action_class = SetInstanceDetailsAction
    contributes = ("source_type", "source_id", "name", "count", "flavor", 
		    "cloud")

    def prepare_action_context(self, request, context):
        if 'source_type' in context and 'source_id' in context:
            context[context['source_type']] = context['source_id']
        return context

    def contribute(self, data, context):
        context = super(SetInstanceDetails, self).contribute(data, context)
        # Allow setting the source dynamically.
        if ("source_type" in context and "source_id" in context
                and context["source_type"] not in context):
            context[context["source_type"]] = context["source_id"]

        # Translate form input to context for source values

        if "source_type" in data:
            context["source_id"] = data.get(data['source_type'], None)
        return context


KEYPAIR_IMPORT_URL = "horizon:nova:access_and_security:keypairs:import"


class SetAccessControlsAction(workflows.Action):
    keypair = forms.DynamicChoiceField(label=_("Keypair"),
                                       required=True,
                                       help_text=_("Which keypair to use for "
                                                   "authentication."),
                                       add_item_link=KEYPAIR_IMPORT_URL)
    groups = forms.MultipleChoiceField(label=_("Security Groups"),
                                       required=False,
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Launch instance in these "
                                                   "security groups."))

    class Meta:
        name = _("Access & Security")
        help_text = _("Control access to your instance via keypairs, "
                      "security groups, and other mechanisms.")

    def populate_keypair_choices(self, request, context):
        try:
            keypairs = api.nova.keypair_list(request)
            if 'cloud' in request.GET:
	        context['cloud'] = request.GET['cloud']
	    if 'cloud' in context:
		cloud = context['cloud']
		keypair_list = [(kp.name, kp.name) for kp in keypairs
				if get_cloud(kp) == cloud]
	    else:
                keypair_list = [(kp.name, kp.name) for kp in keypairs]
        except:
            keypair_list = []
            exceptions.handle(request,
                              _('Unable to retrieve keypairs.'))
        if keypair_list:
            keypair_list.insert(0, ("", _("Select a keypair")))
        else:
            keypair_list = (("", _("No keypairs available.")),)
        return keypair_list

    def populate_groups_choices(self, request, context):
        try:
            groups = api.nova.security_group_list(request)
#            if 'cloud' in request.GET:
#                cloud = request.GET['cloud']
#		security_group_list = [(sg.name, sg.name) for sg in groups
#				if get_cloud(sg) == cloud]
#            else:
            security_group_list = [(sg.name, sg.name) for sg in groups]
        except:
            exceptions.handle(request,
                              _('Unable to retrieve list of security groups'))
            security_group_list = []
        return security_group_list


class SetAccessControls(workflows.Step):
    action_class = SetAccessControlsAction
    depends_on = ("project_id", "user_id", "cloud")
    contributes = ("keypair_id", "security_group_ids")

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['security_group_ids'] = post.getlist("groups")
            context['keypair_id'] = data.get("keypair", "")
        return context


class CustomizeAction(workflows.Action):
    customization_script = forms.CharField(widget=forms.Textarea,
                                           label=_("Customization Script"),
                                           required=False,
                                           help_text=_("A script or set of "
                                                       "commands to be "
                                                       "executed after the "
                                                       "instance has been "
                                                       "built (max 16kb)."))

    class Meta:
        name = _("Post-Creation")
        help_text_template = ("nova/instances/"
                              "_launch_customize_help.html")


class PostCreationStep(workflows.Step):
    action_class = CustomizeAction
    contributes = ("customization_script",)


class LaunchInstance(workflows.Workflow):
    slug = "launch_instance"
    name = _("Launch Instance")
    finalize_button_name = _("Launch")
    success_message = _('Launched %(count)s named "%(name)s".')
    failure_message = _('Unable to launch %(count)s named "%(name)s".')
    success_url = "horizon:nova:instances:index"
    default_steps = (SelectProjectUser,
                     SetInstanceDetails,
                     SetAccessControls,
                     #VolumeOptions,
                     PostCreationStep)

    def format_status_message(self, message):
        name = self.context.get('name', 'unknown instance')
        count = self.context.get('count', 1)
        if int(count) > 1:
            return message % {"count": _("%s instances") % count,
                              "name": name}
        else:
            return message % {"count": _("instance"), "name": name}

    def handle(self, request, context):
        custom_script = context.get('customization_script', '')

        # Determine volume mapping options
        if context.get('volume_type', None):
            if(context['delete_on_terminate']):
                del_on_terminate = 1
            else:
                del_on_terminate = 0
            mapping_opts = ("%s::%s"
                            % (context['volume_id'], del_on_terminate))
            dev_mapping = {context['device_name']: mapping_opts}
        else:
            dev_mapping = None

        try:
            api.nova.server_create(request,
                                   context['cloud'].lower() + '-' + context['name'],
                                   context['source_id'],
                                   context['flavor'],
                                   context['keypair_id'],
                                   normalize_newlines(custom_script),
                                   context['security_group_ids'],
                                   dev_mapping,
                                   instance_count=int(context['count']))
            return True
        except:
            exceptions.handle(request)
            return False
