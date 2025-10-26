from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import calendar
from datetime import datetime, date
from collections import defaultdict
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
import json
from .models import PersonalGoal
from django.contrib.auth.decorators import login_required
# Create your views here.
def _month_nav(year:int, month:int):
    prev_y, prev_m = (year-1, 12) if month == 1 else (year, month-1)
    next_y, next_m = (year+1, 1) if month == 12 else (year, month+1)
    return prev_y, prev_m, next_y, next_m

@login_required(login_url='/login/')
def calendar_today(request):
    today = datetime.now()
    return calendar_month(request, today.year, today.month)

@login_required(login_url='/login/')
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
        'next_year': next_year
    }
    
    return render(request, 'PersonalGoals.html', context)

def add_goal(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only.")
    
    # Handle both form data and JSON
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        title = (data.get("title") or "").strip()
        date_str = data.get("date") or ""
    else:
        title = (request.POST.get("title") or "").strip()
        date_str = request.POST.get("date") or ""
    
    if not title or not date_str:
        if request.content_type == 'application/json':
            return JsonResponse({"error": "Title and date are required.", "success": False}, status=400)
        return HttpResponseBadRequest("Title and date are required.")
    
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        if request.content_type == 'application/json':
            return JsonResponse({"error": "Invalid date format.", "success": False}, status=400)
        return HttpResponseBadRequest("Invalid date format.")
    
    goal = PersonalGoal.objects.create(user=request.user, title=title, date=d)
    
    if request.content_type == 'application/json':
        return JsonResponse({
            "success": True,
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "date": goal.date.isoformat(),
                "is_completed": goal.is_completed
            }
        })
    
    return redirect("goals:calendar_month", year=d.year, month=d.month)

@require_POST
def toggle_goal(request, goal_id:int):
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

@require_POST
def delete_goal(request, goal_id):
    try:
        goal = PersonalGoal.objects.get(id=goal_id, user=request.user)
        goal.delete()
        return JsonResponse({'success': True})
    except PersonalGoal.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Goal not found'})

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