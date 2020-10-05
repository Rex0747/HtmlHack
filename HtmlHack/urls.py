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
from pedidos import views as v2
from stocks import views as v3

from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

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
    path('addFotos',v1.AñadirFotosArticulos ),
    path('verGaleria',v1.verGaleria ),
    path('verqr',v1.mostrarCodigoQR),
    path('verqr2',v1.mostrarCodigoGRpng),
    path('cqr',v1.verCgr),
    path('pedidos/', v2.pedido),
    path('stocks/<modo>' , v3.Stocks),
    path('imprimirEtiquetas/<gfh>', v2.imprimirEtiquetas),
    path('pedidodc/<data>', v2.pedidodc),


]

if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
