from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.calendar_today, name='calendar_today'),
    path('<int:year>/<int:month>/', views.calendar_month, name='calendar_month'),
    path('calendar_data/<int:year>/<int:month>/', views.get_calendar_data, name='get_calendar_data'),
    path("add_goal/", views.add_goal, name="add_goal"),
    path("toggle/<int:goal_id>/", views.toggle_goal, name="toggle_goal"),
    path("delete/<int:goal_id>/", views.delete_goal, name="delete_goal"),
    path("goals/<int:year>/<int:month>/<int:day>/", views.get_goals_for_date, name="get_goals_for_date"),
    path('delete_goal/<int:goal_id>/', views.delete_goal, name='delete_goal'),
]