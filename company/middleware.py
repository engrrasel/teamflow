from django.shortcuts import redirect

class CompanySetupMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not request.user.is_authenticated:
            return self.get_response(request)

        membership = getattr(request, "membership", None)

        if not membership:
            return self.get_response(request)

        company = membership.company

        # ⚠️ safe url_name
        url_name = None
        if request.resolver_match:
            url_name = request.resolver_match.url_name

        # ✅ IMPORTANT: allowed URLs
        allowed_urls = [
            "company_edit",
            "company_holiday",
            "logout",
        ]

        # =========================
        # 1️⃣ Setup not complete
        # =========================
        if not company.is_setup_complete:

            # 👉 already setup page এ থাকলে allow
            if url_name == "company_edit":
                return self.get_response(request)

            return redirect("company_edit")

        # =========================
        # 2️⃣ Setup complete BUT holiday not done
        # =========================
        if not company.holiday_setup_done:

            # 👉 শুধু dashboard block করবে
            if url_name == "dashboard":
                return redirect("company_holiday")

        return self.get_response(request)