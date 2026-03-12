from django.urls import path
from . import views

urlpatterns = [

    # Admin task list
    path("", views.task_list_view, name="task_list"),

    # Add task
    path("add/", views.task_add_view, name="task_add"),

    # Employee dashboard
    path("my/", views.my_tasks_view, name="my_tasks"),

    # Assignment actions
    path("<int:assignment_id>/check-in/", views.check_in_view, name="check_in"),
    path("<int:assignment_id>/order/", views.add_order_view, name="add_order"),
    path("<int:assignment_id>/collection/", views.add_collection_view, name="add_collection"),
    path("<int:assignment_id>/submit/", views.submit_task, name="submit_task"),
    path("<int:assignment_id>/approve/", views.approve_task, name="approve_task"),

    path("tasks/<int:task_id>/", views.task_detail_view, name="task_detail"),

    # Task management
    path("<int:task_id>/edit/", views.task_edit_view, name="task_edit"),
    path("<int:task_id>/delete/", views.task_delete_view, name="task_delete"),

    # Leaderboard
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),

    # Scheduled tasks
    path("scheduled/", views.scheduled_tasks_view, name="scheduled_tasks"),

    # Toggle active/pause
    path("toggle/<int:task_id>/", views.task_toggle, name="task_toggle"),

    # Live GPS Tracking
    path("live-map/", views.live_employee_map, name="live_employee_map"),
    path("update-location/", views.update_employee_location, name="update_location"),

    # Reject / Resubmit
    path("<int:assignment_id>/reject/", views.reject_task, name="reject_task"),
    path("<int:assignment_id>/resubmit/", views.resubmit_task, name="resubmit_task"),

    path("scheduled/<int:task_id>/", views.scheduled_task_detail, name="scheduled_task_detail"),

]