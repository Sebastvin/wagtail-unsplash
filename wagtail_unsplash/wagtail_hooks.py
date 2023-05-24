from django.urls import include, re_path
from wagtail.admin.menu import MenuItem
from wagtail import hooks
from django.urls import reverse_lazy

from wagtail_unsplash.views.admin import search_unsplash_images


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        re_path(
            r"^unsplash-search/$", search_unsplash_images, name="search_unsplash_images"
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_search_unsplash_images_admin_menu_item():
    return MenuItem("Unsplash Images", reverse_lazy("search_unsplash_images"))
