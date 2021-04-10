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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from hacked import views as v0
from configuraciones import views as v1
from pedidos import views as v2
from stocks import views as v3

from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from HtmlHack import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('htmlhack/', include(urls)),
    path('vermeta/',v0.vermeta),
    path('index/' , v0.hack ),
    path('video/', v0.video , { 'plantilla': 'video.html','id':'djangorjar' }, ),
    path('envfichero/', v0.envfichero, { 'plantilla': 'parrafos.html','id':'envfichero'}, ),
    path('config1/', v1.config1 ),
    path('', v0.localhost, name='indice'),
    path('df', v1.download_file),
    path('uf', v1.upload_file),
    path('articulos',v1.articulosAdd),
    path('addgfh',v1.gfhsAdd ),
    path('adddisp',v1.dispositivosAdd ),
    path('gfhdispAdd',v1.adDispGfh ),
    path('hospitalAdd',v1.addHospital ),
    path('addFotos',v1.AñadirFotosArticulos ),
    path('verGaleria',v1.verGaleria ),
    path('verqr',v1.mostrarCodigoQR),
    path('verqr2',v1.mostrarCodigoGRpng),
    path('cqr',v1.verCgr),
    path('mfoto',v1.mfoto),
    path('pedido/', v2.pedido),
    path('stocks/<modo>' , v3.Stocks),
    path('expdisp/<disp>', v2.imprimirEtiquetas),
    #path('addEtiqueta', v2.addLineaEtiqueta),
    path('pedidodc/<data>', v2.pedidodc ),
    path('impresion/',v2.impresion ),
    path('selarticulo', v1.selarticulo ),
    path('actPactos', v1.ActualizarPactos ),
    path('gestPedidos', v2.gestPedidos),
    path('gestPedidosDC', v2.gestPedidosDC ),
    path('gpedidos', v2.gpedidos),
    path('gpedidosdc', v2.gpedidosdc),
    path('getHospital', v1.getHospital ),  #ajax 
    path('getUgs', v1.getUgs ),            #ajax
    path('getConf', v1.getConf ),          #ajax
    path('getPedTemp', v2.getPedTemp ),    #ajax
    path('getAlbaranes', v2.getAlbaranes ),#ajax
    path('getAlbaranesdc', v2.getAlbaranesdc),#ajax
    path('getLineas', v2.getLineas ),      #ajax  
    
]

if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
