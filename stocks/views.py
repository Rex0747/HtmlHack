from django.shortcuts import render
from django.http import HttpResponse
from stocks.models import prueba
from configuraciones.models import articulos, hospitales
from pedidos.models import pedidos_ident, pedidos
from django.http import HttpResponseRedirect
import json
# Create your views here.

def Stocks( request , modo):
    dato = request.POST.get('dato')
    items = modo.split('|')
    for i in items:
        dat=prueba(prb=i)
        dat.save()

    return render( request, 'stocks.html',{'mode': modo ,'dato': dato})
    #return response(dato)

def calcularConsumo( request ):
    if request.method == 'GET' and request.GET.get('codigo',False) and request.GET['cal_ini'] and request.GET['cal_fin']:

        txtJson = None
        bloque = "["
        codigo = request.GET['codigo']
        f_ini = request.GET['cal_ini']
        f_fin = request.GET['cal_fin']

        art = articulos.objects.get(codigo=codigo)
        pfechas = pedidos_ident.objects.filter(fecha__range=[f_ini,f_fin])

        mtx = []
        for i in pfechas:
            mtx.append(i.pedido)

        pedido = pedidos.objects.filter(npedido__in=mtx,hospital=hospitales.objects.get(codigo=request.session['hospitalCodigo'])).filter(codigo=art.pk)

        if len(pedido) > 0:
            for i in pedido:
                fechaPedido = pedidos_ident.objects.get(pedido=i.npedido).fecha
                fecha = str(fechaPedido.day) + '-' + str(fechaPedido.month) + '-' + str(fechaPedido.year) + ' ' + str(fechaPedido.hour) + ':' + str(fechaPedido.minute)
                bloque += '{"cantidad": "%s", "codigo": "%s" , "nombre": "%s" ,"disp": "%s", "gfh": "%s", "npedido": "%s", "hospital": "%s", "fecha": "%s"} ,'\
                    %(i.cantidad, i.codigo.codigo,  i.codigo.nombre, i.disp.nombre, i.gfh.gfh, i.npedido, i.hospital.codigo, fecha )
        else:
            bloque += '{"cantidad": "%s"},' %(len(pedido))

        res = bloque[ :-1] + "]"
        print('JSON: ', res)
        j = json.loads(res, strict=False)
        txtJson = json.dumps(j)
        #print( 'JSON: ', txtJson)
        
        return HttpResponse(txtJson)
    else:
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        else:
            request.session.set_expiry (request.session['tiempo'])
            print('TIEMPO SESION: ', str(request.session.get_expiry_age()))
            return render(request, 'stockReferencia.html')

