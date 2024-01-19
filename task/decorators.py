from django.shortcuts import redirect

def staff_login_redirect(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('/staff/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view