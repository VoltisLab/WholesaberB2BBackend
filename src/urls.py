"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from test_views import test_view
from simple_test import health_check
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import uuid
import os

from graphene_django.views import GraphQLView
from graphene_file_upload.django import FileUploadGraphQLView

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        try:
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                file_extension = os.path.splitext(image_file.name)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = default_storage.save(f'profile_images/{unique_filename}', image_file)
                image_url = request.build_absolute_uri(f'/media/{file_path}')
                return JsonResponse({'success': True, 'image_url': image_url, 'message': 'Image uploaded successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'No image file provided'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Upload failed: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Only POST method allowed'}, status=405)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", health_check, name='health'),
    path("test/", test_view, name='test'),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("graphql/uploads/", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    path("api/upload-image/", upload_image, name='upload_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)