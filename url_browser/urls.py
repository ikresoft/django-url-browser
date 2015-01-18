from django.conf.urls import patterns, url
from views import form_view, url_image, set_image, set_file


urlpatterns = patterns('',
    url(r'^form-view/$', form_view, name='url-browser'),
    url(r'set-image/$', set_image, name='filer-set-image'),
    url(r'set-file/$', set_file, name='filer-set-file'),
    url(r'url-image/(?P<image_id>\d+)/$', url_image, name='filer-url-image'),
    url(r'url-image/(?P<image_id>\d+)/(?P<thumb_options>\d+)/$', url_image, name='filer-url-image'),
    url(r'url-image/(?P<image_id>\d+)/(?P<width>\d+)/(?P<height>\d+)/$', url_image, name='filer-url-image'),
)
