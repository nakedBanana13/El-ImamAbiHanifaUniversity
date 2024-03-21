from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse


class ApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated and is not approved
        if request.user.is_authenticated and not request.user.is_superuser:
            if not request.user.is_approved:
                # Redirect to the not approved view
                logout(request)
                return redirect(reverse('under_review'))
        return self.get_response(request)


class DocumentAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(settings.MEDIA_URL):
            user = request.user
            if not user.is_superuser:
                # Extract document type from URL
                document_type = request.path.split('/')[-2]
                if document_type not in ['certificates', 'ids']:
                    return HttpResponseForbidden("Access Forbidden")

                # Extract username from URL
                username = request.path.split('/')[-3]
                if username != user.username:
                    return HttpResponseForbidden("Access Forbidden")
        return self.get_response(request)