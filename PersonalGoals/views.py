from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import calendar
from datetime import datetime, date
from collections import defaultdict
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST
import json
from .models import PersonalGoal
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.templatetags.static import static

# Create your views here.
def _month_nav(year:int, month:int):
    prev_y, prev_m = (year-1, 12) if month == 1 else (year, month-1)
    next_y, next_m = (year+1, 1) if month == 12 else (year, month+1)
    return prev_y, prev_m, next_y, next_m

@login_required()
def calendar_today(request):
    today = datetime.now()
    return calendar_month(request, today.year, today.month)

@login_required()
def calendar_month(request, year, month):
    # Get calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Calculate previous and next month/year
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Get goals for this month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    goals = PersonalGoal.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lt=end_date
    )

    # Format goals by date
    goals_by_date = {}
    for goal in goals:
        date_str = goal.date.strftime('%Y-%m-%d')
        if date_str not in goals_by_date:
            goals_by_date[date_str] = []
        goals_by_date[date_str].append({
            'id': goal.id,
            'title': goal.title,
            'is_completed': goal.is_completed
        })

    context = {
        'today': datetime.now().strftime('%Y-%m-%d'),
        'today_day': datetime.now().day,
        'current_month': datetime.now().month,
        'current_year': datetime.now().year,
        'year': year,
        'month': month,
        'month_name': month_name,
        'calendar': cal,
        'goals_by_date': goals_by_date,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    
    return render(request, 'PersonalGoals.html', context)

@login_required()
@csrf_exempt
@require_POST
def add_goal(request):
    # Handle both form data and JSON - ALWAYS return JSON for API requests
    try:
        # Try to parse JSON first
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            title = (data.get("title") or "").strip()
            date_str = data.get("date") or ""
        else:
            # For form data (what Flutter sends)
            title = (request.POST.get("title") or "").strip()
            date_str = request.POST.get("date") or ""
        
        # Check if it's an API request (Flutter, mobile, or AJAX)
        is_api_request = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.content_type == 'application/json' or
            request.headers.get('Accept', '').startswith('application/json') or
            'flutter' in request.headers.get('User-Agent', '').lower()
        )
        
        if not title or not date_str:
            error_msg = "Title and date are required."
            if is_api_request:
                return JsonResponse({"error": error_msg, "success": False}, status=400)
            return HttpResponseBadRequest(error_msg)
        
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            error_msg = "Invalid date format."
            if is_api_request:
                return JsonResponse({"error": error_msg, "success": False}, status=400)
            return HttpResponseBadRequest(error_msg)
        
        goal = PersonalGoal.objects.create(user=request.user, title=title, date=d)
        
        # ALWAYS return JSON for API requests
        if is_api_request:
            return JsonResponse({
                "success": True,
                "goal": {
                    "id": goal.id,
                    "title": goal.title,
                    "date": goal.date.isoformat(),
                    "is_completed": goal.is_completed
                }
            })
        
        # Only redirect for web form submissions
        return redirect("goals:calendar_month", year=d.year, month=d.month)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON.", "success": False}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e), "success": False}, status=500)

@login_required()
@csrf_exempt
@require_POST
def toggle_goal(request, goal_id: int):
    goal = get_object_or_404(PersonalGoal, id=goal_id, user=request.user)
    goal.is_completed = not goal.is_completed
    goal.save()
    
    if request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            "success": True,
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "date": goal.date.isoformat(),
                "is_completed": goal.is_completed
            }
        })
    
    return redirect("goals:calendar_month", year=goal.date.year, month=goal.date.month)

@login_required()
@csrf_exempt
@require_POST
def delete_goal(request, goal_id):
    try:
        goal = PersonalGoal.objects.get(id=goal_id, user=request.user)
        goal.delete()
        return JsonResponse({'success': True})
    except PersonalGoal.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Goal not found'})

@login_required()
def get_goals_for_date(request, year: int, month: int, day: int):
    """Get goals for a specific date via AJAX"""
    try:
        target_date = date(year, month, day)
    except ValueError:
        return JsonResponse({"error": "Invalid date."}, status=400)
    
    goals = PersonalGoal.objects.filter(user=request.user, date=target_date).order_by('id')
    
    goals_data = []
    for goal in goals:
        goals_data.append({
            "id": goal.id,
            "title": goal.title,
            "date": goal.date.isoformat(),
            "is_completed": goal.is_completed
        })
    
    return JsonResponse({
        "success": True,
        "date": target_date.isoformat(),
        "goals": goals_data
    })

@login_required()
def get_calendar_data(request, year, month):
    user = request.user
    # Get the calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get goals for this month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    goals = PersonalGoal.objects.filter(
        user=user,
        date__gte=start_date,
        date__lt=end_date
    )

    # Format goals by date
    goals_by_date = {}
    for goal in goals:
        date_str = goal.date.strftime('%Y-%m-%d')
        if date_str not in goals_by_date:
            goals_by_date[date_str] = []
        goals_by_date[date_str].append({
            'id': goal.id,
            'title': goal.title,
            'is_completed': goal.is_completed
        })

    return JsonResponse({
        'success': True,
        'data': {
            'calendar': cal,
            'month_name': month_name,
            'month': month,
            'year': year,
            'goals': goals_by_date
        }
    })