from django.shortcuts import render
from configuraciones.models import articulos, configurations
from pedidos.models import pedidos, usuarios
from django.db import connection

# Create your views here.
global hospital, disp, user, gfh

def pedido( request ):
    global gfh, hospital, disp, user
    pedid='' ; pedido='' ; lista=[] ; codes={}
    if request.method == 'POST':

        clavesDescartar = ['csrfmiddlewaretoken', 'hospital', 'gfh', 'disp', 'pboton', 'tped', 'user']
        claves = request.POST.keys()
        for i in claves:
            if i in clavesDescartar:
                pass
            else:
                lista.append(i)
        #print('lista: '+ str(lista))
        for i in lista:
            if int(request.POST[i]) > 0:
                codes[i] = request.POST[i] 

        




        if request.POST['gfh'] and request.POST['hospital'] and request.POST['disp'] and request.POST['user']:
            hospital = request.POST['hospital']
            gfh = request.POST['gfh']
            disp = request.POST['disp']
            user = request.POST['user']
            print('User: ' + user + '\t'+ 'disp: ' + disp + '\t'+ 'gfh: ' + gfh + '\t'+ 'hosp: ' + hospital )

            cursor = connection.cursor()
            cursor.execute('SELECT gfh_id FROM configuraciones_dispositivos WHERE nombre = %s ', [ disp ])
            gfh_id = cursor.fetchone()[0]
            print('gfh_id: '+str(gfh_id))
            cursor.execute('SELECT gfh FROM configuraciones_gfhs WHERE id = %s ', [ gfh_id ])
            gfh = cursor.fetchone()[0]
            print('gfh: '+str(gfh))
            cursor.execute('SELECT id FROM configuraciones_dispositivos WHERE nombre = %s', [ disp ])
            disp_id = cursor.fetchone()[0]
            print('disp_id:'+str(disp_id))
            cursor.execute('SELECT id from pedidos_usuarios WHERE ident = %s', [ user ]) 
            print(str(cursor))
            user_id = cursor.fetchone()[0]
            print('disp_id:'+str(user_id))

            datos = configurations.objects.filter(gfh=gfh_id, disp=disp_id, hosp_id=2).order_by('modulo','estanteria','ubicacion').distinct()
            #consulta = 'SELECT * FROM configuraciones_configurations WHERE gfh ='+str(gfh_id)+' and disp =' +str(disp_id)+ ' and hosp_id = 2'
            #cursor.execute( consulta)
            #datos = cursor.fetchone()[0]
            
            print('Type: '+ str(type(datos)))
            print(str( datos ))

            return render( request, 'pedidos.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user, 'datos': datos })


        if request.method == 'POST':
            print(str(codes.keys()) + '\t' + str(codes.values()))


        return render( request, 'pedido2.html',{ 'hospital': hospital, 'gfh': gfh, 'disp': disp, 'user': user }) 

    else:

        

        return render( request, 'pedidos.html')
