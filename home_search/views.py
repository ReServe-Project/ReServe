# home_search/views.py

from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Class, CATEGORY_CHOICES
from .forms import ClassForm
from .utils import is_instructor   # ← use the ONE canonical checker


# --------------------------- Pages ---------------------------

def home(request):
    """
    Home page: show some classes (or all).
    Pass categories for the horizontal scroller chips on the home page.
    """
    classes = Class.objects.all().order_by("-id")
    ctx = {
        "classes": classes,
        "categories": CATEGORY_CHOICES,
        "show_create_button": is_instructor(request.user),
    }
    return render(request, "home_search/home.html", ctx)


# Accept ?category=<key> where key is one of CATEGORY_CHOICES
ALIASES = {
    "ice": "ice-skating",
    "ice skating": "ice-skating",
    "muay-thai": "muaythai",
    "muay thai": "muaythai",
}

def search(request):
    qs = Class.objects.all().order_by("-id")

    # Normalize category param and filter if valid
    category = (request.GET.get("category") or "").strip().lower().replace(" ", "-")
    category = ALIASES.get(category, category)
    valid = {k for k, _ in CATEGORY_CHOICES}
    if category in valid:
        qs = qs.filter(category=category)

    flag = is_instructor(request.user)
    print(f"[/search] user={getattr(request.user,'username',request.user)} | is_instructor={flag}")

    return render(request, "home_search/search.html", {
        "classes": qs,
        "categories": CATEGORY_CHOICES,
        "active_category": category,
        "show_create_button": flag,
    })


# --------------------------- CRUD views ---------------------------

class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_authenticated and obj.owner_id == self.request.user.id


class ClassDetailView(DetailView):
    model = Class
    template_name = "home_search/class_detail.html"
    context_object_name = "c"


class ClassCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Class
    form_class = ClassForm
    template_name = "home_search/class_form.html"
    success_url = reverse_lazy("home_search:search")

    def test_func(self):
        # Only instructors may access
        allowed = is_instructor(self.request.user)
        print(f"[create] user={getattr(self.request.user,'username',self.request.user)} is_instructor={allowed}")
        return allowed

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = CATEGORY_CHOICES
        ctx["is_edit"] = False
        return ctx


class ClassUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Class
    form_class = ClassForm
    template_name = "home_search/class_form.html"
    success_url = reverse_lazy("home_search:search")

    def test_func(self):
        return self.get_object().owner_id == self.request.user.id

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = CATEGORY_CHOICES
        ctx["is_edit"] = True
        return ctx


class ClassDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Class
    template_name = "home_search/class_confirm_delete.html"
    success_url = reverse_lazy("home_search:search")  # back to the grid
