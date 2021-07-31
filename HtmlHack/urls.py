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
#login
from django.contrib.auth.views import LoginView, logout_then_login
#______________RESTFULL_______________
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'_pedidos', v2.PedidosViewSet, basename='_pedidos')


urlpatterns = [
    path('admin/', admin.site.urls, name = 'admin'),
    #path('accounts/login/',LoginView.as_view(template_name = 'login.html'),name='log'), #login
    #path('accounts/logout/',logout_then_login, name = 'logout'),
    #path('htmlhack/', include(urls)),
    path('logout',v0.logout_request, name='_logout'),
    path('login',v0.login_request, name='_login'),
    path('selhospital',v0.selHospital, name='_selhospital'),
    path('vermeta/',v0.vermeta),
    path('index/' , v0.hack , name = 'index'),
    #path('login' , v0.login ),
    path('video/', v0.video , { 'plantilla': 'video.html','id':'djangorjar' }, ),
    path('envfichero/', v0.envfichero, { 'plantilla': 'parrafos.html','id':'envfichero'}, ),
    path('config1/', v1.config1 ),
    #path('', v0.localhost, name='indice'),
    path('df', v1.download_file, name = 'dowf'),
    path('uf', v1.upload_file, name = 'uplf'),
    path('articulos',v1.articulosAdd),
    path('addgfh',v1.gfhsAdd ),     #comprobar sino borrar url  vista  y plantilla
    path('adddisp',v1.dispositivosAdd ),   #comprobar sino borrar url  vista  y plantilla
    path('gfhdispAdd',v1.adDispGfh ),
    path('hospitalAdd',v1.addHospital ),
    path('addFotos',v1.AñadirFotosArticulos ),    #comprobar sino borrar url  vista  y plantilla
    path('verGaleria',v1.verGaleria ),            #comprobar sino borrar url  vista  y plantilla
    path('verqr',v1.mostrarCodigoQR),             #comprobar sino borrar url  vista  y plantilla
    path('verqr2',v1.mostrarCodigoGRpng),         #comprobar sino borrar url  vista  y plantilla
    path('cqr',v1.verCgr),                        #comprobar sino borrar url  vista  y plantilla
    path('mfoto',v1.mfoto),                       #comprobar sino borrar url  vista  y plantilla
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
    path('filtrardatos', v1.filtrardatos, name = 'filtrar'),
    path('getHospital', v1.getHospital ),  #ajax 
    path('getUgs', v1.getUgs ),            #ajax
    path('getConf', v1.getConf ),          #ajax
    path('getPedTemp', v2.getPedTemp ),    #ajax
    path('getAlbaranes', v2.getAlbaranes ),#ajax
    path('getAlbaranesdc', v2.getAlbaranesdc),#ajax
    path('getLineas', v2.getLineas ),      #ajax  
    path('getDatosHospital', v1.getDatosHospital ), #ajax
    path('getConfGfh', v1.getConfGfh, name='getconfgfh'), #ajax
    path('addLineaPedidoDc', v2.addLineaPedidoDc, name='addLineaPedido'), #ajax
    path('stockref', v3.calcularConsumo, name= 'calconsumo'), #ajax

    path('ret', include(router.urls)),#rest_framework
    path('rest_pedido/', include('rest_framework.urls', namespace='rest_framework.urls')),

]

if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
