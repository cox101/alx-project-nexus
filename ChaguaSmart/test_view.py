from django.http import JsonResponse

def test_view(request):
    return JsonResponse({"status": "ok", "message": "Test view is working"})