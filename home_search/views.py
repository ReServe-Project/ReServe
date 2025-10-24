# home_search/views.py
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Class, CATEGORY_CHOICES

# Display labels + stable keys for URLs / DB
CATEGORY_CHOICES = [
    ("yoga", "Yoga"),
    ("pilates", "Pilates"),
    ("dance", "Dance"),
    ("boxing", "Boxing"),
    ("muaythai", "Muaythai"),
    ("ice-skating", "Ice Skating"),  # renamed
]

# Backward-compat: old links/data
ALIASES = {
    "ice": "ice-skating",
    "ice skating": "ice-skating",
    "muay-thai": "muaythai",
    "muay thai": "muaythai",
}

def home(request):
    """
    Home page: show some classes (or all).
    Pass categories for the horizontal scroller chips on the home page.
    """
    classes = Class.objects.all().order_by("-id")  # tweak as you like
    ctx = {
        "classes": classes,
        "categories": CATEGORY_CHOICES,   # << correct var
    }
    return render(request, "home_search/home.html", ctx)


def search(request):
    qs = Class.objects.all().order_by("-id")

    # read and normalize category from querystring
    category = (request.GET.get("category") or "").strip().lower().replace(" ", "-")
    category = ALIASES.get(category, category)

    # filter only if it's a valid category
    valid_cats = {k for k, _ in CATEGORY_CHOICES}
    if category and category in valid_cats:
        qs = qs.filter(category=category)

    return render(request, "home_search/search.html", {
        "classes": qs,
        "categories": CATEGORY_CHOICES,   # list of (key, label)
        "active_category": category,      # used by template to highlight
    })