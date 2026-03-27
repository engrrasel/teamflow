from django.http import HttpResponseForbidden

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):

        membership = getattr(request, "membership", None)

        if not membership or membership.role != "admin":
            return HttpResponseForbidden("Access denied")

        return view_func(request, *args, **kwargs)

    return wrapper