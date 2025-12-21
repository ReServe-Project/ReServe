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
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from urllib.parse import urlparse
import urllib.request
import ssl



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

def _class_to_dict(c: Class, user=None):
    """
    JSON shape that matches your Flutter FitnessClass.fromJson
    """
    return {
        "id": c.id,
        "owner": c.owner.username if c.owner_id else None,
        "name": c.name,
        "category": c.category,
        "price": c.price,
        "image_url": c.image_url or "",
        "description": c.description or "",
        "datetime": c.datetime.isoformat() if c.datetime else None,
        "location": c.location or "",
        # OPTIONAL but very helpful for your UI:
        "is_owner": bool(user and user.is_authenticated and c.owner_id == user.id),
    }


@require_http_methods(["GET"])
def api_classes_list(request):
    """
    GET /home_search/api/classes/?category=yoga&q=beginner
    Return list JSON for Flutter.
    """
    qs = Class.objects.all().order_by("-id")

    # optional filtering by category (same idea as your search view)
    category = (request.GET.get("category") or "").strip().lower().replace(" ", "-")
    valid = {k for k, _ in CATEGORY_CHOICES}
    if category in valid:
        qs = qs.filter(category=category)

    # optional search
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(location__icontains=q)
        )

    data = [_class_to_dict(c, request.user) for c in qs]
    return JsonResponse(data, safe=False)


@require_http_methods(["GET"])
def api_class_detail(request, pk: int):
    """
    GET /home_search/api/classes/<id>/
    """
    try:
        c = Class.objects.get(pk=pk)
    except Class.DoesNotExist:
        return JsonResponse({"message": "Not found"}, status=404)

    return JsonResponse(_class_to_dict(c, request.user), safe=False)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_class_create(request):
    """
    POST /home_search/api/classes/create/
    Instructor only.
    Body JSON:
    {name, category, price, image_url, description, datetime, location}
    """
    if not is_instructor(request.user):
        return JsonResponse({"message": "Forbidden: instructor only"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = request.POST  # fallback if sent as form

    name = (payload.get("name") or "").strip()
    category = (payload.get("category") or "").strip()
    price = payload.get("price")
    image_url = (payload.get("image_url") or "").strip()
    description = (payload.get("description") or "").strip()
    location = (payload.get("location") or "").strip()
    raw_dt = payload.get("datetime")

    if not name:
        return JsonResponse({"message": "name is required"}, status=400)

    valid = {k for k, _ in CATEGORY_CHOICES}
    if category not in valid:
        return JsonResponse({"message": "invalid category"}, status=400)

    try:
        price_int = int(price)
    except Exception:
        return JsonResponse({"message": "price must be int"}, status=400)

    dt = None
    if raw_dt:
        dt = parse_datetime(str(raw_dt))  # expects ISO format

    c = Class.objects.create(
        owner=request.user,
        name=name,
        category=category,
        price=price_int,
        image_url=image_url,
        description=description,
        datetime=dt,
        location=location,
    )

    return JsonResponse({"success": True, "data": _class_to_dict(c, request.user)}, status=201)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_class_update(request, pk: int):
    """
    POST /home_search/api/classes/<id>/update/
    Owner only.
    """
    try:
        c = Class.objects.get(pk=pk)
    except Class.DoesNotExist:
        return JsonResponse({"message": "Not found"}, status=404)

    if c.owner_id != request.user.id:
        return JsonResponse({"message": "Forbidden: owner only"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = request.POST

    # Update only provided fields
    if "name" in payload:
        c.name = (payload.get("name") or "").strip()

    if "category" in payload:
        category = (payload.get("category") or "").strip()
        valid = {k for k, _ in CATEGORY_CHOICES}
        if category not in valid:
            return JsonResponse({"message": "invalid category"}, status=400)
        c.category = category

    if "price" in payload:
        try:
            c.price = int(payload.get("price"))
        except Exception:
            return JsonResponse({"message": "price must be int"}, status=400)

    if "image_url" in payload:
        c.image_url = (payload.get("image_url") or "").strip()

    if "description" in payload:
        c.description = (payload.get("description") or "").strip()

    if "location" in payload:
        c.location = (payload.get("location") or "").strip()

    if "datetime" in payload:
        raw_dt = payload.get("datetime")
        c.datetime = parse_datetime(str(raw_dt)) if raw_dt else None

    c.save()
    return JsonResponse({"success": True, "data": _class_to_dict(c, request.user)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_class_delete(request, pk: int):
    """
    POST /home_search/api/classes/<id>/delete/
    Owner only.
    """
    try:
        c = Class.objects.get(pk=pk)
    except Class.DoesNotExist:
        return JsonResponse({"message": "Not found"}, status=404)

    if c.owner_id != request.user.id:
        return JsonResponse({"message": "Forbidden: owner only"}, status=403)

    c.delete()
    return JsonResponse({"success": True})


@require_GET
def api_image_proxy(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponse("Missing url", status=400)

    # only allow http/https (basic safety)
    if not (url.startswith("http://") or url.startswith("https://")):
        return HttpResponse("Invalid url", status=400)

    try:
        # DEV ONLY: bypass SSL verification
        ctx = ssl._create_unverified_context()

        req = urllib.request.Request(
            url,
            headers={
                # helps some hosts allow the request (Pinterest sometimes)
                "User-Agent": "Mozilla/5.0",
                "Referer": url,
            },
        )

        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            content = resp.read()
            content_type = resp.headers.get("Content-Type", "image/jpeg")

        return HttpResponse(content, content_type=content_type)

    except Exception as e:
        print("[image-proxy] ERROR:", repr(e))
        return HttpResponse("Bad Gateway", status=502)
