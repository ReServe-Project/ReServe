from django.db.models import Q, Avg, Count
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Class, CATEGORY_CHOICES
from .forms import ClassForm
from .utils import is_instructor  
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from product_details.models import Review



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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # reviews queryset
        context["reviews"] = Review.objects.filter(class_item=self.object)

        # compute and expose average rating (do not need to persist here)
        avg = Review.objects.filter(class_item=self.object).aggregate(avg=Avg('rating'))['avg'] or 0
        self.object.average_rating = round(avg, 1)

        # build per-star counts (1..3 scale used in templates)
        qs = Review.objects.filter(class_item=self.object).values('rating').annotate(count=Count('id'))
        rating_summary = {i: 0 for i in range(1, 4)}
        total_reviews = 0
        for row in qs:
            r = int(row['rating'])
            c = row['count']
            if 1 <= r <= 3:
                rating_summary[r] = c
                total_reviews += c

        context["rating_summary"] = rating_summary
        context["total_reviews"] = total_reviews

        # existing user_review logic
        user_review = None
        user = self.request.user
        if user.is_authenticated:
            try:
                user_review = Review.objects.get(class_item=self.object, user=user)
            except Review.DoesNotExist:
                user_review = None

        context["user_review"] = user_review
        return context

class AjaxFormMixin:
    ajax_template_name = None  # set in subclass

    def get_template_names(self):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest" and self.ajax_template_name:
            return [self.ajax_template_name]
        return [self.template_name]

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Re-render the modal with errors (still HTML)
            return render(
                self.request,
                self.get_template_names()[0],
                self.get_context_data(form=form),
                status=400,
            )
        return super().form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "redirect_url": self.get_success_url(),
                }
            )
        return response


class AjaxDeleteMixin:
    ajax_template_name = None

    def get_template_names(self):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest" and self.ajax_template_name:
            return [self.ajax_template_name]
        return [self.template_name]

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "redirect_url": success_url,
                }
            )
        return HttpResponseRedirect(success_url)


class ClassCreateView(LoginRequiredMixin, UserPassesTestMixin, AjaxFormMixin, CreateView):
    model = Class
    form_class = ClassForm
    template_name = "home_search/class_form.html"
    ajax_template_name = "home_search/class_form_modal.html"
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


class ClassUpdateView(LoginRequiredMixin, UserPassesTestMixin, AjaxFormMixin, UpdateView):
    model = Class
    form_class = ClassForm
    template_name = "home_search/class_form.html"
    ajax_template_name = "home_search/class_form_modal.html"
    success_url = reverse_lazy("home_search:search")

    def test_func(self):
        return self.get_object().owner_id == self.request.user.id

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = CATEGORY_CHOICES
        ctx["is_edit"] = True
        return ctx


class ClassDeleteView(LoginRequiredMixin, OwnerRequiredMixin, AjaxDeleteMixin, DeleteView):
    model = Class
    template_name = "home_search/class_confirm_delete.html"
    ajax_template_name = "home_search/class_confirm_delete_modal.html"
    success_url = reverse_lazy("home_search:search")
