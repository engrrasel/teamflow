from django.urls import path
from . import views

urlpatterns = [


# ========================
# TASK LIST / DASHBOARD
# ========================
path("", views.task_list_view, name="task_list"),
path("my/", views.my_tasks_view, name="my_tasks"),

# ========================
# TASK MANAGEMENT
# ========================
path("add/", views.task_add_view, name="task_add"),
path("<int:task_id>/edit/", views.task_edit_view, name="task_edit"),
path("<int:task_id>/delete/", views.task_delete_view, name="task_delete"),
path("tasks/<int:task_id>/", views.task_detail_view, name="task_detail"),

# ========================
# ASSIGNMENT DETAIL (🔥 MAIN FIX)
# ========================
path("assignment/<int:assignment_id>/", views.assignment_detail_view, name="assignment_detail"),
path("assignment/<int:assignment_id>/edit/", views.assignment_edit_view, name="assignment_edit"),
path("assignment/<int:assignment_id>/delete/", views.assignment_delete_view, name="assignment_delete"),
path("check-in/<int:assignment_id>/", views.check_in_assignment, name="check_in_assignment"),
# ========================
# ASSIGNMENT ACTIONS
# ========================
path("<int:assignment_id>/order/", views.add_order_view, name="add_order"),
path("<int:assignment_id>/collection/", views.add_collection_view, name="add_collection"),
path("<int:assignment_id>/submit/", views.submit_task, name="submit_task"),
path("<int:assignment_id>/approve/", views.approve_task, name="approve_task"),
path("<int:assignment_id>/reject/", views.reject_task, name="reject_task"),

# ========================
# LEADERBOARD
# ========================
path("leaderboard/", views.leaderboard_view, name="leaderboard"),

# ========================
# SCHEDULED TASKS
# ========================
path("scheduled/", views.scheduled_tasks_view, name="scheduled_tasks"),
path("scheduled/<int:task_id>/", views.scheduled_task_detail, name="scheduled_task_detail"),
path("toggle/<int:task_id>/", views.task_toggle, name="task_toggle"),

# ========================
# LIVE TRACKING
# ========================
path("live-map/", views.live_employee_map, name="live_map"),
path("update-location/", views.update_employee_location, name="update_location"),
path("locations/", views.employee_locations_api, name="employee_locations_api"),

]
