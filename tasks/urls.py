from django.urls import path
from . import views

urlpatterns = [

    path("", views.task_list_view, name="task_list"),

    path("add/", views.task_add_view, name="task_add"),

    path("my/", views.my_tasks_view, name="my_tasks"),

    path("<int:task_id>/check-in/", views.check_in_view, name="check_in"),

    path("<int:task_id>/order/", views.add_order_view, name="add_order"),

    path("<int:task_id>/collection/", views.add_collection_view, name="add_collection"),

    path("<int:task_id>/edit/", views.task_edit_view, name="task_edit"),

    path("<int:task_id>/delete/", views.task_delete_view, name="task_delete"),

    path("<int:task_id>/submit/", views.submit_task, name="submit_task"),

    path("<int:task_id>/approve/", views.approve_task, name="approve_task"),

    path("leaderboard/", views.leaderboard_view, name="leaderboard"),

]