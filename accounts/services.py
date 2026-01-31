from .models import Membership


def can_manage_company(membership):
    return membership.role in ['company_admin', 'platform_admin']
