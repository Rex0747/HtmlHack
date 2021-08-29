from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from hacked.contenido import contenido
from hacked.models import datos, enlaces
from configuraciones.models import hospitales

#"<br><iframe id='vid1' width='640' height='480' src='https://www.youtube.com/embed/t7zQhKXEdbI' ></iframe>",'titulocont':'EL TIGRE DE MALASIA' }

def hack( request ):
	request.session['hospital'] = "HCSC"
	request.session['user'] = "Rex" 

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

def localhost( request ):

	return HttpResponse('ESTAS EN LOCALHOST.')

def login_request( request ):
	# if request.method == 'POST':
	# 	usuario = request.POST['login']
	# 	passwd = request.POST['passwd']
	# 	if usuario == "rex" and passwd == "perikillo":
	# 		request.session['user'] = usuario
	# 		request.session.set_expiry (360)
	# 		print(request.session.get_expiry_age())
	# 		return render(request, 'index.html')
	# 	else:
	# 		return render( request, "login.html")
	#return render( request, "login.html")
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		print(form)
		if form.is_valid():
			user = form.cleaned_data.get("username")
			passwd = form.cleaned_data.get("password")
			usuario = authenticate(username=user,password=passwd)
			if user is not None:
				login(request, usuario)
				request.session['tiempo'] = 3600
				request.session.set_expiry (request.session['tiempo'])
				request.session['user'] = user
				messages.success(request, f"Logeado como {user}")
				print(f"Logeado como {user}")
				print('TIEMPO SESION: ', str(request.session.get_expiry_age()))
				return HttpResponseRedirect("selhospital")
			else:
				messages.error(request, "Login incorrecto")
				print("Login incorrecto")
		else:
			messages.error(request, "Login incorrecto")
			print("Login incorrecto2")
	form = AuthenticationForm()
	form.fields['username'].widget.attrs['placeholder'] = 'INTRODUCE USUARIO'
	form.fields['password'].widget.attrs['placeholder'] = 'INTRODUCE CONTRASEÑA'
	return render(request, "login.html", {"form": form})

def logout_request(request):
	logout(request)
	messages.info(request, "Sesion cerrada")
	return HttpResponseRedirect("login")

def selHospital(request):
	hospital = ''
	if request.method == 'POST':
		hospital = request.POST['hosp']
		hospital2 = hospitales.objects.get(codigo=hospital)
		print('HOSPITAL: ', hospital2)
		request.session['hospital'] = hospital2.nombre
		request.session['hospitalCodigo'] = hospital2.codigo
		return redirect('dowf')
		#return HttpResponseRedirect('df')
		#return render(request, "BajarConfig.html",{'hospital': hospital2})
	
	hospitalesAll = hospitales.objects.all()

	return render(request, "sel_hospital.html",{'hospitales': hospitalesAll})