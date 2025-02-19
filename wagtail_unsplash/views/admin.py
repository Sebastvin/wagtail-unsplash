import json
import os
import urllib.request

from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from wagtail.admin.forms.search import SearchForm
from wagtail.images import get_image_model

from wagtail_unsplash.api import api

Image = get_image_model()


def search_unsplash_images(request):
    if request.POST and "image_id" in request.POST:
        image = add_unsplash_image_to_wagtail(request.POST["image_id"])
        return redirect(reverse("wagtailimages:edit", args=(image.id,)))

    print("*" * 100)
    print(request.POST)

    query_string = None
    if "q" in request.GET:
        form = SearchForm(request.GET, placeholder=_("Search Unsplash"))
        if form.is_valid():
            query_string = form.cleaned_data["q"]
    else:
        form = SearchForm(placeholder=_("Search Unsplash"))

    page = int(request.GET.get("p", 1))
    per_page = 25

    response = None
    if query_string:
        response = api.search.photos(query=query_string, page=page, per_page=per_page)

    context = {
        "search_form": form,
        "results": None,
    }

    if response:
        total_pages = response["total_pages"]
        next_page = None
        if page != total_pages:
            next_page = page + 1
        previous_page = None
        if page != 0:
            previous_page = page - 1

        context.update(
            current_page_number=total_pages,
            current_page=page,
            total_results=response["total"],
            results=response["results"],
            next_page=next_page,
            previous_page=previous_page,
        )

    return TemplateResponse(request, "wagtail_unsplash/search.html", context)


def add_unsplash_image_to_wagtail(image_id):
    photo = api.photo.get(image_id)

    url = photo.urls.raw
    unsplash_image = urllib.request.urlretrieve(url)

    with open(unsplash_image[0], "rb") as fp:
        image_obj = Image.objects.create(
            title=f"Unsplash image ({photo.id})",
            file=File(fp),
            width=photo.width,
            height=photo.height,
        )
        return image_obj
