"""HtmlHack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from hacked import views as v0
from configuraciones import views as v1

urlpatterns = [
    path('admin/', admin.site.urls),
    path('vermeta/',v0.vermeta),
    path('index/' , v0.hack ),
    path('video/', v0.video , { 'plantilla': 'video.html','id':'djangorjar' }, ),
    path('envfichero/', v0.envfichero, { 'plantilla': 'parrafos.html','id':'envfichero'}, ),
    path('config1/', v1.config1 ),
    path('uploadfile', v1.upload_file),
    path('downloadfile', v1.download_file),
    path('articulos',v1.articulosAdd),
    path('addgfh',v1.gfhsAdd ),
    path('adddisp',v1.dispositivosAdd ),
    
  
]

if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
