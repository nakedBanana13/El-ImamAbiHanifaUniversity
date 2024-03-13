from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


@login_required
def course_chat_room(request, course_id):
    try:
        user = request.user
        if user.is_student:
            course = request.user.student_profile.courses_joined.get(id=course_id)
        else:
            course = request.user.instructor_profile.courses_created.get(id=course_id)
    except Exception as e:
        return HttpResponseForbidden()
    return render(request, 'chat/room.html', {'course': course})
