from django.utils import six
from django.forms import forms as newforms
from django.http import HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import get_urlconf, get_resolver
from forms import *
from url_browser import form_registry
from filer.models import Image, File
import json


#  load all urlnames
def form_view(request):
    apps = {}
    apps['Other'] = {}
    media = newforms.Media()

    known_url_names = []

    def _stack_known_urls(reverse_dict, ns=None):
        for url_name, url_rules in reverse_dict.items():
            if isinstance(url_name, six.string_types):
                if ns is not None:
                    url_name = '%s:%s' % (ns, url_name)
                known_url_names.append(url_name)

    #  urls
    resolver = get_resolver(get_urlconf())
    for ns, (url_prefix, ns_resolver) in resolver.namespace_dict.items():
        if ns != 'admin':
            _stack_known_urls(ns_resolver.reverse_dict, ns)
    _stack_known_urls(resolver.reverse_dict)

    if request.method == 'POST':
        for app, forms in form_registry.get_apps().items():
            apps[app] = {}
            for url_name, form in forms.items():
                apps[app][request.POST.get('url_name')] = form(url_name, request.POST)
                if apps[app][request.POST.get('url_name')].is_valid():
                    if request.is_ajax():
                        return HttpResponse(apps[app][request.POST.get('url_name')].submit(), content_type="text/plain")
    else:
        for app, forms in form_registry.get_apps().items():
            apps[app] = {}
            for url_name, form in forms.items():
                known_url_names.remove(url_name)
                apps[app][url_name] = form(url_name)
                media += apps[app][url_name].media
        for url in known_url_names:
            apps['Other'][url] = None
    context = {
        'title': 'URL Browser',
        'apps': apps,
        'is_popup': request.GET.get('_popup', '') != '',
        'media': media,
        'image_form': ImageForm(),
        'file_form': FileForm(),
    }
    return render(request, "url_browser/app_list.html", context)


def get_image_dict(image_id, thumb_options=None, width=None, height=None):
    image = Image.objects.get(pk=image_id)
    filer_id = image.pk
    url = image.url
    description = image.default_alt_text
    thumbnail_options = {}
    if thumb_options is not None:
        thumbnail_options = ThumbnailOption.objects.get(pk=thumb_options).as_dict

    if width is not None or height is not None:
        width = int(width)
        height = int(height)

        size = (width, height)
        thumbnail_options.update({'size': size})

    if thumbnail_options != {}:
        thumbnailer = image.easy_thumbnails_thumbnailer
        image = thumbnailer.get_thumbnail(thumbnail_options)
        url = image.url
    data = {
        'url': url,
        'filer_id': filer_id,
        'description': description,
        'width': image.width,
        'height': image.height,
    }
    return data


def url_image(request, image_id, thumb_options=None, width=None, height=None):
    return HttpResponse(json.dumps(get_image_dict(image_id, thumb_options, width, height)), content_type="application/json")


def set_image(request):
    if request.method == "POST":
        form = ImageForm(request.POST)
        if form.is_valid():
            return render(
                request,
                "url_browser/filer_done.html",
                {
                    "url": get_image_dict(
                        form.cleaned_data["image"],
                        form.cleaned_data["thumbnail_option"],
                        form.cleaned_data["width"],
                        form.cleaned_data["height"]
                    )["url"],
                    "ckeditor_param": form.cleaned_data["ckeditorfuncnum"],
                }
            )


def set_file(request):
    if request.method == "POST":
        form = FileForm(request.POST)
        if form.is_valid():
            return render(
                request,
                "url_browser/filer_done.html",
                {
                    "url": File.objects.get(pk=form.cleaned_data["file"]).url,
                    "ckeditor_param": form.cleaned_data["ckeditorfuncnum"],
                }
            )
