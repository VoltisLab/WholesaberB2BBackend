from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    return JsonResponse({
        'status': 'success',
        'message': 'AWS Elastic Beanstalk Django backend is working!',
        'method': request.method,
        'path': request.path
    })
