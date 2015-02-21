from django.forms import forms, models, widgets, fields
from django.contrib.admin.templatetags.admin_static import static
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from filer.models import File
from filer import settings as filer_settings

from models import ThumbnailOption

import logging
logger = logging.getLogger(__name__)


class BaseUrlForm(forms.Form):
    url_name = fields.CharField(widget=widgets.HiddenInput())

    def __init__(self, url_name, *args, **kwargs):
        super(BaseUrlForm, self).__init__(*args, **kwargs)
        self.url_name = url_name
        self.fields["url_name"].initial = self.url_name

    def submit(self):
        pass

    def get_url_name(self):
        return self.url_name

    class Media:
        js = (static('admin/js/%s' % 'admin/RelatedObjectLookups.js'),)

    class Meta:
        verbose_name = 'BaseUrlForm'


class FileWidget(widgets.HiddenInput):

    def render(self, name, value, attrs=None):
        obj = self.obj_for_value(value)
        css_id = attrs.get('id', 'id_image_x')
        css_id_thumbnail_img = "%s_thumbnail_img" % css_id
        css_id_description_txt = "%s_description_txt" % css_id
        related_url = None
        if value:
            try:
                file_obj = File.objects.get(pk=value)
                related_url = file_obj.logical_folder.get_admin_directory_listing_url_path()
            except Exception as e:
                # catch exception and manage it. We can re-raise it for debugging
                # purposes and/or just logging it, provided user configured
                # proper logging configuration
                if filer_settings.FILER_ENABLE_LOGGING:
                    logger.error('Error while rendering file widget: %s', e)
                if filer_settings.FILER_DEBUG:
                    raise
        if not related_url:
            related_url = reverse('admin:filer-directory_listing-last')
        params = None  # self.url_parameters()
        if params:
            lookup_url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in list(params.items())])
        else:
            lookup_url = ''
        if 'class' not in attrs:
            # The JavaScript looks for this hook.
            attrs['class'] = 'vForeignKeyRawIdAdminField'
        output = [super(widgets.HiddenInput, self).render(name, value, attrs)]
        if value:
            output.append(self.label_for_value(value))
        hidden_input = mark_safe(''.join(output))
        filer_static_prefix = filer_settings.FILER_STATICMEDIA_PREFIX
        if not filer_static_prefix[-1] == '/':
            filer_static_prefix += '/'
        context = {
            'hidden_input': hidden_input,
            'lookup_url': '%s%s' % (related_url, lookup_url),
            'thumb_id': css_id_thumbnail_img,
            'span_id': css_id_description_txt,
            'object': obj,
            'lookup_name': name,
            'filer_static_prefix': filer_static_prefix,
            'clear_id': '%s_clear' % css_id,
            'id': css_id,
        }
        html = render_to_string('url_browser/widgets/admin_file.html', context)
        return mark_safe(html)

    def obj_for_value(self, value):
        obj = None
        return obj

    class Media:
        js = (filer_settings.FILER_STATICMEDIA_PREFIX + 'js/popup_handling.js',)


class ImageForm(forms.Form):
    image = fields.IntegerField(widget=FileWidget())
    thumbnail_option = models.ModelChoiceField(queryset=ThumbnailOption.objects.all(), required=False)
    use_autoscale = fields.BooleanField(required=False)
    width = fields.IntegerField(required=False)
    height = fields.IntegerField(required=False)
    crop = fields.BooleanField(required=False)
    upscale = fields.BooleanField(required=False)
    front_image = fields.BooleanField(required=False)
    ckeditorfuncnum = fields.IntegerField(widget=widgets.HiddenInput(), required=False)


class FileForm(forms.Form):
    file = fields.IntegerField(widget=FileWidget())
    ckeditorfuncnum = fields.IntegerField(widget=widgets.HiddenInput(), required=False)
