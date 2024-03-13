from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class ApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated and is not approved
        if request.user.is_authenticated and not request.user.is_active and not request.user.is_approved:
            if not request.user.is_superuser:
                # Redirect to the not approved view
                logout(request)
                return redirect(reverse('under_review'))
        return self.get_response(request)