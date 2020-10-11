from django.shortcuts import render
from django.http import HttpResponse
from hacked.contenido import contenido
from hacked.models import datos, enlaces

#"<br><iframe id='vid1' width='640' height='480' src='https://www.youtube.com/embed/t7zQhKXEdbI' ></iframe>",'titulocont':'EL TIGRE DE MALASIA' }




def hack( request ):
	c = contenido()
	contexto = c.v2()
	return render(request,'index.html',{'title': 'HACKED' ,'ticont':'INTROSERVER', 'context': contexto , 'titulocont': 'PARRAFO DE PRUEBA' })    #HACKEDMATTE{
	
def video( request , plantilla, id ):
	contexto= datos.objects.filter(idsel= id).values()
	contexto = contexto[0]
	return render( request, plantilla , {'title': contexto['titulo'], 'ticont': contexto['titulo_cont'], 'context': contexto['dato'],'titulocont': contexto['nombre_pagina'] } )
	
def envfichero( request , plantilla , id ):
	contexto = datos.objects.filter(idsel= id).values() #devuelve lista de diccionarios
	contexto = contexto[0]  #al seleccionar solo un registro nos quedamos con la primera lista
	#print( 'Entregado : ' + str( contexto))
	return render( request, plantilla , {'title': contexto['titulo'], 'ticont': contexto['titulo_cont'], 'context': contexto['dato'],'titulocont': contexto['nombre_pagina'] } )

def vermeta( request ):
	valor = request.META.items()
	#valor.sort()
	return render( request , 'request_items.html',{'context': valor ,'titulo_cont': 'Atributos de request.META'})

