from django.shortcuts import render
from stocks.models import prueba

# Create your views here.

def Stocks( request , modo):
    dato = request.POST.get('dato')
    items = modo.split('|')
    for i in items:
        dat=prueba(prb=i)
        dat.save()

    return render( request, 'stocks.html',{'mode': modo ,'dato': dato})
    #return response(dato)
