from accounts.models import Membership

class MembershipMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.membership = None

        if request.user.is_authenticated:
            membership = (
                Membership.objects
                .select_related('company')
                .filter(user=request.user)
                .first()
            )
            request.membership = membership

        return self.get_response(request)
