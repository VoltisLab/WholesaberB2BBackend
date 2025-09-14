from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_view(request):
    return JsonResponse({
        'status': 'success',
        'message': 'Django backend is working!',
        'method': request.method
    })
