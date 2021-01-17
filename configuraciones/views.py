#import os
from django.http import HttpResponseRedirect
from django.template import Template 
from django.shortcuts import render
from django.http import HttpResponse , Http404, JsonResponse
from configuraciones.models import  articulos , configurations , gfhs , dispositivos, hospitales, excel
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm
from os import remove , listdir , mkdir
from configuraciones.excell import Excell
from configuraciones.excell import comprobarExcel
#from configuraciones.excell import ListaToQuerySet
#from configuraciones.excell import list_to_queryset
from itertools import chain
from HtmlHack.settings import MEDIA_ROOT
from HtmlHack.settings import STATIC_ROOT
from django.db import connection, transaction
from django.db.models import Q
#from configuraciones.qrcode import generate
#from configuraciones.qrcode import make
import qrcode
import glob
import traceback

from configuraciones.func import funcConf, Json

#from somewhere import handle_uploaded_file
# Create your views here.

hosp_update = None
g_gfh = None
g_conf = None


def config1( request ):
    contexto = { 'titulo': 'Configuraciones', 'dato': 'ESTA ES UNA NUEVA CONFIGURACION.'}
    return render( request ,'ini.html', contexto )

@transaction.atomic
def upload_fileNew(request):

    file_url =None
    borradas=None
    nfilas = None
    a = None #articulo
    d = None #dispositivo
    h = None #hospital
    g = None #gfh

    if request.method == 'POST' and request.FILES['upload']:
        fichero = request.FILES['upload']
        rta = glob.glob(MEDIA_ROOT+'/*.xlsx')
        for f in rta:
            remove(f)
        
        fs = FileSystemStorage()
        filename = fs.save( fichero.name , fichero  )
        file_url = fs.url( filename )
        
        conf = None
        dispo = None
        gfh = None

        if '.xlsx' in fichero.name:
            excel1 = Excell( MEDIA_ROOT +'/' + fichero.name )
            nfilas = str( excel1.getnumerofilas() -1 )
            listaExcel = excel1.leer_fichero2() #lista leida por el excel
            if len( listaExcel) == 0:
                return HttpResponse('Numero incorrecto de columnas.')
            #print('ListaExcel: ' + str(listaExcel))
            #_______________________COMPROBAR EXCEL______________________________________
            columnas = ''; vacios = [] ; duplicados = []; gfhdisp = []
            comprobar = comprobarExcel( listaExcel )

            columnas = excel1.getnumerocolumnas()
            print('Ncolumnas: '+str(columnas))

            v = comprobar.comprobarVacios()
            if len( v ) > 1:
                vacios = v

            dup = comprobar.comprobarDuplicados( ) 
            if len( dup ) > 0:
                duplicados = dup

            gfh = comprobar.comprobarGfhDisp()
            if len( gfh ) > 0:
                gfhdisp = gfh

            # com = comprobar.comprobar_DC()

            #return HttpResponse(com)
            if (columnas < 12) or (len( vacios ) > 1) or (len( duplicados ) > 0) or (len( gfh ) > 0):
                #print('Columnas: ' + str(columnas) + '  Vacios: '+ str( vacios) + '  Duplicados: '+str(duplicados) + '  GfhD: '+ str(gfhdisp))
                remove( MEDIA_ROOT +'/' + fichero.name )
                return render( request, 'error.html', {'columnas': columnas, 'vacios': vacios, 'duplicados': duplicados ,'gfh': gfhdisp,})
                
            #endregion 
            try:
                dispo = dispositivos.objects.filter( nombre=listaExcel[0].dispositivo)[0] # objeto dispositivo
                #gfh = gfhs.objects.filter( nombre=dispo.nombre)[0] # objeto gfh
                
                hosp_id = getIdDB( hospitales.objects.filter(codigo=listaExcel[0].hospital),'id')
                gfh = gfhs.objects.get(nombre=dispo.nombre,hp_id=hosp_id)
                    
            except Exception as e:
                #return HttpResponse('No esta configurado el gfh '+str(listaExcel[0].gfh))
                return render( request, 'SubirConfig.html', {'error':'GFH '+str(listaExcel[0].gfh)+' no configurado'})

#            idconfig = GetAleatorio() #mejorar para evitar colision.
            idconfig = funcConf.SetMaxId()
            borradas = excel.objects.filter( gfh=gfh.id, disp=dispo.id ).delete()[0]
            #borradas = configurations.objects.filter( gfh=gfh.id, disp=dispo.id ).delete()[0]
            #A la espera de implantar historico de configuraciones.
            print('Filas Borradas: ', str(borradas))
            
            for itm in listaExcel:
                try:
                    d = dispositivos.objects.get(nombre=itm.dispositivo)
                    h = hospitales.objects.get(codigo=itm.hospital)
                    g = gfhs.objects.get(gfh=itm.gfh, nombre=itm.dispositivo)
                    a = articulos.objects.get(codigo=itm.codigo, hospital=h)
                    
                except Exception as e:
                    a = articulos(codigo=itm.codigo, nombre=itm.nombre, hospital=h, foto='articulos/fotos-'+h.codigo+'/'+itm.codigo+'.png')
                    a.save()
                    print('Se inserto articulo nuevo. ' )

                try:
                    a = articulos.objects.get(codigo=itm.codigo, hospital=h)
                    #print('Articulo: '+str(a))
                    conf = configurations(modulo=itm.modulo,estanteria=itm.estanteria,ubicacion=itm.ubicacion,division=itm.division,\
                        codigo=itm.codigo,nombre=a,pacto=itm.pacto,minimo=itm.minimo,dc=itm.dc,gfh=g,disp=d,hosp=h,nconfig=idconfig)
                    conf.save()


                    conf = excel(modulo=itm.modulo,estanteria=itm.estanteria,ubicacion=itm.ubicacion,division=itm.division,\
                        codigo=itm.codigo,nombre=a,pacto=itm.pacto,minimo=itm.minimo,dc=itm.dc,gfh=g,disp=d,hosp=h)
                    conf.save()

                except Exception as e:
                    print('Hubo un fallo.', str(e))
                    #transaction.rollback()

    return render(request, 'SubirConfig.html', {'uploaded_file': file_url , 'borradas': borradas, 'nfilas': nfilas })


def download_file(request):
    retorno = []
    nlineas = ''
    res = ''
    gfhId = ''
    gfhNombre = ''
    articulo = None
    dispId = ''
    dispositivo = ''
    hospital = ''
    code = ''
    cqr = ''
    nombre = ''
    dispdown = ''
    #global gfhdispdown

    cqrlist = {}
    if  request.method == 'POST':
        if request.POST['gfh']:
            gfhNombre = request.POST['gfh']
        if request.POST['disp']:
            dispositivo = request.POST['disp']
        if request.POST['code']:
            code = request.POST['code']
        if request.POST['hosp']:
            hospital = request.POST['hosp']
        if gfhNombre:
            dispdown = gfhNombre
        if dispositivo:
            dispdown = dispositivo
        if code:
            dispdown = code

        #__________________________________SQL___________________________________________
        try:
            #_____________Hospital______________
            hospital_id = hospitales.objects.get(codigo=hospital).pk
            #___________________________________
            
            if dispositivo:
                gfhNombre =  gfhs.objects.get(nombre=dispositivo).gfh
                #print('GFH_nombre: '+str(gfhNombre))
                gfhId = gfhs.objects.get( nombre=dispositivo, gfh=gfhNombre).pk
                #print('GFH_id: '+str(gfhId))
                dispId = dispositivos.objects.get(nombre=dispositivo).pk
                #print('IdDisp:'+str(dispId))
                gfhNombre = None

            if gfhNombre:
                
                gfhId =  gfhs.objects.filter(gfh=gfhNombre)[0].pk
                #gfhId = gfhs.objects.get( gfh=gfhNombre).pk
                #gfhId = gfhs.objects.get(gfh=gfhNombre, nombre=dispositivo).pk
                #print( 'gfh_id3: '+ str(gfhId))
                #dtmp = dispositivos.objects.get(gfh=gfhId).nombre
                #print('dispNombre: '+str(dtmp))
                #gfhId = dispositivos.objects.get(nombre=dtmp).gfh
                #print('gfh_id4: '+ str(gfhId))
                #_________________________numero de mismo codigo en DB_____________________________
                
                #__________________________________________________________________________________
            
            if code and not dispositivo: # and not gfhNombre:
                print('Entro en code')
                res = excel.objects.filter(  codigo=code ,hosp=hospital_id ).order_by('gfh','modulo','estanteria','ubicacion')
            elif dispositivo and code:
                print('Entro en dispositivo and code  ' + str(dispId) + ' '+code )
                res = excel.objects.filter( disp=dispId, codigo=code ,hosp=hospital_id ).order_by('modulo','estanteria','ubicacion')
            elif gfhNombre and code:
                print('Entro en gfhNombre and code  ' + gfhNombre + ' ' + code )
                res = excel.objects.filter( gfh=gfhId , codigo=code ,hosp=hospital_id ).order_by('modulo','estanteria','ubicacion')
            elif dispositivo:
                print('Entro en dispositivo  ' + str(dispId) )
                res = excel.objects.filter( disp=dispId ,hosp=hospital_id ).order_by('modulo','estanteria','ubicacion')
            elif gfhNombre:
                print('Entro en gfhNombre  ' + gfhNombre + '  '+str(gfhId) )
                res = excel.objects.filter( gfh=gfhId ,hosp=hospital_id).order_by('disp','modulo','estanteria','ubicacion')  
            

        except Exception as e:
            print('Excepcion en fase 1.' + str( e ))
            print('TraceBack: ', traceback.format_exc())
        
        
        nlineas = 'NUMERO DE LINEAS: ' + str( len(res))
        print('NUMERO DE LINEAS: ' + str( len(res)))
        #print('RES: '+str(res))
        excelf = Excell( dispdown ) #Excell( 'data' )
        ultimaFila = 2
        #repes = None
        num = 0
        for i in res:
            #print('objeto i: ' + str(i))
            #cod = articulos.objects.filter(idsel=i.nombre_id, hospital_id=hospital_id).values('codigo')[0].get('codigo')
            cod = articulos.objects.filter(idsel=i.nombre_id).values('codigo')[0].get('codigo')
            #print('cod: '+ str(cod))
            num = articulos.objects.filter( codigo=cod  ).count()
            if num > 1:
                #print('Numero de ids de articulo: ' + str(num) + ' en id: '+ str(cod)) 
                repes = articulos.objects.filter(codigo=cod, hospital_id=hospital_id)[0]
                #print(str(repes.nombre))
                
            try:
                articulo = getIdDB(articulos.objects.filter(idsel=i.nombre_id , hospital_id=hospital_id), 'nombre')
                #print('objeto articulo: ' + str(articulo) + ' idsel: '+ str(i.nombre_id))
                if num > 1:
                    articulo = getIdDB(articulos.objects.filter(codigo=cod , hospital_id=hospital_id), 'nombre')
                    #articulo.nombre = repes.nombre
                    #print('Se cambio de nombre a codigo: ' +cod+ ' a: '+ repes.nombre )
            except Exception as e:
                print('Excepcion en nombre articulo: ' + str(e) )
                print('articulo: ' + str(articulo))
                

            dispositivo = getIdDB(dispositivos.objects.filter(id=i.disp.id), 'nombre')
            gfhNombre = getIdDB(gfhs.objects.filter(id=i.gfh.id), 'gfh')
            
            cqr = str(i.modulo)+'-'+str(i.estanteria)+'-'+str(i.ubicacion)+'-'+str(i.division)+'|'+str(i.codigo)+'|'+str(articulo)+\
            '|'+str(i.pacto)+'|'+str(i.minimo)+'|'+str(i.dc)+'|'+str(gfhNombre)+'|'+str(dispositivo)+'|'+str(hospital )
            cqrlist.update({ i.codigo : cqr })
            #_________________________________________________________________________
            ret = []
            ret.append(i.modulo)
            ret.append(i.estanteria)
            ret.append(i.ubicacion )
            ret.append(i.division )
            ret.append(i.codigo )
            ret.append( articulo ) #i.nombre_id
            ret.append(i.pacto )
            ret.append(i.minimo )
            ret.append(i.dc )
            ret.append( gfhNombre )
            ret.append( dispositivo )
            ret.append( hospital ) #hospitalP
            ret.append( cqr )
            retorno.append( ret )
# ____________FASE LLENAR EXCEL____________________
            excelf.insertar_rangofila( ret , ultimaFila , 1 )
            ultimaFila += 1
            ret = None
        #print('Retorno: ' + str(retorno))
        ret = ['modulo','estanteria','ubicacion','division','codigo',
        'nombre','pacto','minimo','dc','gfh','disp','hosp_id']
        excelf.insertar_rangofila( ret , 1 , 1 )
        excelf.salvarexcell2()
        #excelf.cambiarcolorfila(1 ,1 ,'yellow','yellow')
# ____________END FASE LLENAR EXCEL________________
# ____________FASE DOWNLOAD FILA____________________        
        #print( excel.nombre )
        fila = MEDIA_ROOT +'/' + dispdown + '.xlsx' #'data.xlsx'
        #print('FilaExcel: '+ fila)
        if 'bajarfila' in request.POST:
            import os
            with open( fila , 'rb') as fh:
                #print('ENTRO')
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename( fila )
                #remove( fila )
                return response
        try:
            remove( fila )  #eliminamos fichero del servidor.
        except Exception as e:
            print('No existe fichero '+ str(e) )
# ____________END FASE DOWNLOAD FILA____________________
    hospitalAll = hospitales.objects.all()
    return render(request, 'BajarConfig.html', {'configuraciones': retorno,
    'nombre': gfhNombre, 'lineas': nlineas , 'cqr': cqrlist, 'hospitales': hospitalAll  })
    

def articulosAdd(request):
    #print( MEDIA_ROOT +'/' + 'articulos.xlsx' )
    excel = None
    excel = Excell( MEDIA_ROOT +'/' + 'articulos.xlsx' )# , 'Hoja1')
    nfilas = str( excel.getnumerofilas() -1 )
    fila = excel.leer_fichero()
    #print( 'Numero de lineas: ' + str( nfilas) )
    #indice = 0
    for item in fila:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM configuraciones_hospitales WHERE codigo = %s',[ item[2] ])
            item[2] = cursor.fetchone()[0]
            #print('ITEM: ' + str( item[0] )  + ' ' + str( item[1] ) + ' ' + str( item[2] )  )
            cursor.execute("INSERT INTO configuraciones_articulos(codigo,nombre,hospital_id ) VALUES ('"+str(item[0])+"','"+str(item[1])+"','"+str(item[2])+"')")
            
            #art = articulos( idsel=str(indice), codigo=item[0], nombre=item[1], hospital=item[2] )
            #art.save()
            #indice += 1
            cursor = None
        except Exception as e:
            return HttpResponse( 'COLISION AL INSERTAR LISTA DE ARTICULOS. ERROR: ' +str(e) )  
    return HttpResponse( 'Lista de articulos añadida correctamente' )

def gfhsAdd(request):
    excel = None
    excel = Excell( MEDIA_ROOT +'/' + 'gfhs.xlsx' )
    nfilas = str( excel.getnumerofilas() -1 )
    fila = excel.leer_fichero()
    #print( 'Numero de lineas: ' + str( nfilas) )
    for item in fila:
        try:
            gfh = gfhs( gfh=item[0], nombre=item[1])
            gfh.save()
        except Exception as e:
            #return HttpResponse( 'Hubo un fallo al subir lista de gfhs. ' +str(e))
            print('COLISION AL INSERTAR gfh: ' + item[0] + ' , ERROR: ' + str( e ) )
    return HttpResponse( 'Lista  gfhs añadida correctamente' )


def dispositivosAdd(request):
    excel = None
    excel = Excell( MEDIA_ROOT +'/' + 'dispositivos.xlsx' )
    nfilas = str( excel.getnumerofilas() -1 )
    fila = excel.leer_fichero()
    #print( 'Numero de lineas: ' + str( nfilas) )
    for item in fila:
        try:
            #______________________________MODO SQL___________________________________
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM configuraciones_gfhs WHERE configuraciones_gfhs.gfh = %s', [item[1]] )

            gfhs = cursor.fetchone()[0]
            cursor = None

            data = dispositivos( nombre=item[0], gfh_id=gfhs )
            data.save()

            #_________________________________________________________________________
        except Exception as e:
            #return HttpResponse( 'Hubo un fallo al subir lista de dispositivos. ' +str(e))
            print('COLISION AL INSERTAR gfh: ' + item[1]+ ' , ERROR: ' + str( e ) )
    return HttpResponse( 'Lista dispositivos correctamente' )

def adDispGfh( request ):
    sound = 0
    gfhss = None
    gfh = None
    disp = None     # tabla disp = gfh_id , nombre
    hosp_id = None  # tabla gfh  = gfh, nombre , hp_id_id
    hosp = hospitales.objects.all()
    #print('Numero Hospitales: ', str(hosp_id))
    if hosp.count() == 0:
        msg = 'Antes de añadir dispositivos y gfhs es necesario crear un hospital.'
        return render(request, 'addDispGfh.html', {'mensaje': msg})
    else:
        pass
        #return render(request, 'addDispGfh.html',{ 'hospital': hosp_id })

    

    if request.method == 'POST':
        if request.POST['addgfhC']:
            gfh = request.POST['addgfhC']
            if request.POST['addHospC']:
                hosp_id = request.POST['addHospC']
            if request.POST['addisp']:
                disp = request.POST['addisp']
                try:
                    dataGfh = gfhs(gfh=gfh, nombre=disp, hp_id_id=hospitales.objects.get(codigo=hosp_id).pk)
                    dataGfh.save()
                    dataDisp = dispositivos(gfh_id=dataGfh.id, nombre=disp)
                    dataDisp.save()
                    sound = 1
                except Exception as e:
                    print('Error al crear gfh/disp.')
                    print(str(e))
    if hosp_id:
        print(hosp_id)
        print(str(hospitales.objects.get(codigo=hosp_id).id))
        gfhss = gfhs.objects.filter(hp_id=hospitales.objects.get(codigo=hosp_id).id).order_by('gfh')
            
    return render(request, 'addDispGfh.html',{'sound': sound, 'gfhs': gfhss, 'hospital': hosp})

def addHospital( request ):
    codigo = None
    hospital = None
    mensaje = None
    hospi = None
    log = None
    lat = None
    comentario = None
    link = None
    foto = 'img/'

    if request.method == 'POST':
        if request.POST['codhosp']:
            codigo = request.POST['codhosp']
            if request.POST['codisp']:
                hospital = request.POST['codisp']
                if request.POST['log']:
                    log = request.POST['log']
                if request.POST['lat']:
                    lat = request.POST['lat']
                if request.POST['foto']:
                    foto += request.POST['foto']
                if request.POST['coment']:
                    comentario = request.POST['coment']
                if request.POST['link']:
                    link = request.POST['link']

                try:
                    ruta = 'articulos/fotos-'+codigo
                    hosp = hospitales(codigo=codigo, nombre=hospital, rutaFotos=ruta, longitud=log, latitud=lat, foto=foto, comentario=comentario, link=link)
                    hosp.save()
                    fila = MEDIA_ROOT +'/' + 'articulos/fotos-'+ ruta
                    mkdir(fila)
                    mensaje = hosp.nombre+' creado correctamente'
                except Exception as e:
                    print('Error al crear hospital.')
                    print(str(e))
    
    hospi = hospitales.objects.all()
    #print('SQL: ', hospi.query)
    print('Hospitales: ', hospi)

    return render(request, 'HospitalAdd.html', {'mensaje': mensaje,'hospitales': hospi} )

def AñadirFotosArticulos( request ):
    ruta = MEDIA_ROOT+'/articulos/'
    filas =  listdir( ruta )
    codigo = ''
    res = '0'
    for i in filas:
        codigo = i.rstrip('.png')
        if not codigo:
            codigo = i.rstrip('.jpg')
        #print('CODIGO: '+codigo + ' RUTA: '+ ruta + i )
        res = addFotoArticulo( str('articulos/' + i) , str(codigo) )
        #print('res: '+res )
        if res == '0':
            #return HttpResponse( 'Ruta fotos añadida correctamente' )
            print('Codigo '+codigo+' añadido correctamente')

    return HttpResponse( res)

def verArticulo( request ):
    img = None
    if request.method == 'POST' and request.POST['verimg']:
        codigo = request.POST['verimg']
        img = articulos.objects.filter(codigo= codigo)[0]
        #print( str(img))
    return render( request , 'galeria.html',{'img': img })

def verGaleria( request ):
    img = ''
    if request.method == 'POST' and request.POST['hospital']:
        hospi = request.POST['hospital']
        try:
            id_hospi = hospitales.objects.get( codigo=hospi )
        except Exception as e:
            img = 'Hospital desconocido.'
            return render( request , 'galeria.html',{'error': img })
        img = articulos.objects.filter(hospital_id=id_hospi)
        #img = articulos.objects.filter(~Q(foto = ''))
        #print('Numero de registros: ' + str(len(img)))
        #print(str('HOSPITAL: '+ hospi))
        return render( request , 'galeria.html',{'imagen': img })
    else:
        img = 'No se selecciono hospital.'
        return render( request , 'galeria.html',{'error': img })

def mostrarCodigoQR( request ):
    img = ''
    if request.method == 'POST' and request.POST['verimg']:
        codigo = request.POST['verimg']
        img = qrcode.make( codigo )
        imagen = open( STATIC_ROOT + 'qrcode.png','wb')
        img.save(imagen)
        imagen.close()
        imagen = open( STATIC_ROOT + 'qrcode.png' ,'rb').read()
        return HttpResponse( imagen, content_type="image/png")

    return render( request , 'galeria.html',{'imagen': img })

def mostrarCodigoGRpng( request ):
    if request.method == 'POST' and request.POST['verimg']:
        valor = request.POST['verimg']
        img = qrcode.make( valor )
        imagen = open( STATIC_ROOT + 'qrcode.png','wb')
        img.save(imagen)
        imagen.close()
        return render( request , 'galeria.html',{'qrcode': STATIC_ROOT + 'qrcode.png' })
    return render( request , 'galeria.html')

def verCgr( request ):
    #items = request.META.items()
    items = request.GET['data']
    #print(str(items))
    fila = items.split('|')
    #print(str(fila) + ' long='+ str(len(fila)))
    codigo = fila[1]
    hospital = fila[8]
    hospital_id = hospitales.objects.filter(codigo=hospital ).values('id')
    print('Hospital_id: ' + str(hospital_id) + ' CODIGO: '+ str(codigo))
    foto = articulos.objects.filter(codigo=codigo, hospital=hospital_id[0].get('id') ) #.values('foto')[0]

    print('RUTA: ' + str(foto))
    img = qrcode.make( items )
    imagen = open( STATIC_ROOT + 'qrcode.png','wb')
    img.save( imagen )
    imagen.close()
    return render( request , 'cqr.html',{'cqr': items , 'qrcode': STATIC_ROOT + 'qrcode.png' ,'img': foto ,} )

def mfoto(request):
    items = request.GET['data']

    foto = articulos.objects.filter( foto=items )
    print(str(items))
    print(str(foto))

    return render(request,'mfoto.html',{'foto': foto} )

def getIdDB( formula, campo ):
    d = formula
    #print(str(d) + ' len: ' +str(len(d)))
    if len(d)==1:
        return d.values(campo)[0].get(campo)
    if len(d)>1:
        return d.values(campo)[0].get(campo)

def addFotoArticulo( rutaNombreFichero , codigo ):

    try:
        p = articulos.objects.filter(codigo=codigo, hospital_id=2 ).update(foto=rutaNombreFichero)
        return '0'
    except Exception as e:
        res = 'Fallo al actualizar: ' + str( e ) + ' Codigo: '+codigo+' Ruta: '+rutaNombreFichero
    return str( res )

def selarticulo( request ):
    nombre = ''
    hospital = ''
    hospi = hospitales.objects.all()

    if request.method == 'POST':
        if request.POST['art']:
            nombre = request.POST['art']
            hospital = request.POST['hospi']
            #print('Hospital: ', hospital )

    hosp_id = getIdDB( hospitales.objects.filter(codigo=hospital),'id' )
    #print( 'Hosp_id: ', hosp_id )
    #cursor = connection.cursor()
    #articulos = cursor.execute('SELECT codigo, nombre, foto from configuraciones_articulos  WHERE nombre LIKE  %s  AND hospital_id = %s ',[ '%'+nombre+'%', hosp_id ])
    if nombre == "":
        nombre = "POQWERYEUUEYEUWYUYWUWYWY"

    try:
        #art = articulos.fetchall()
        art = articulos.objects.filter(nombre__contains=nombre, hospital_id=hosp_id)
        #print(str(art))

    except Exception as e:
        print( 'Error: ', str(e) )

    return render( request , 'selarticulo.html',{ 'articulos': art ,'hospitales': hospi } )

@transaction.atomic
def ActualizarPactos_Back( request ):
    #disp = None
    global g_gfh
    global g_conf
    idconf = None
    hosp_update = hospitales.objects.all()
    if request.method == "POST":
        #print('Hospital: ',request.POST['selHosp']);'  Disp: ',request.POST['selDisp'];'  Gfh: ',request.POST['selGfh']
        if request.POST.get('selHosp', False)==''  and request.POST.get('selGfh', False)=='' and request.POST.get('selDisp', False)=='':
            clavesDescartar = ('csrfmiddlewaretoken', 'selHosp', 'selDisp', 'selGfh' ) #'oculto'
            dic = {}
            for key, value in request.POST.items():
                if key not in clavesDescartar:
                    if value != '':
                        print('VALOR : ' , str(key) + '  ',str(value))
                        dic[str(key)] = int(value)

            #print(dic)
            #print('GFH: ', g_gfh)
            for key, value in dic.items():
                try:
                    mtx = key.split('*')
                    t_excel = excel.objects.get(modulo=mtx[1],estanteria=mtx[2],ubicacion=mtx[3],division=mtx[4],codigo=mtx[0],gfh=g_gfh.id)
                    t_excel.pacto = value
                    t_excel.minimo = value
                    t_excel.save()
                    idconf = funcConf.SetMaxId_gfh(gfhs.objects.get(gfh=g_gfh.gfh,nombre=g_gfh.nombre,hp_id=g_gfh.hp_id).id, dispositivos.objects.get(nombre=g_gfh.nombre).id, g_gfh.hp_id)
                    print('IDCONFIG: ', str(idconf))
                    t_config = configurations.objects.get(modulo=mtx[1],estanteria=mtx[2],ubicacion=mtx[3],division=mtx[4],codigo=mtx[0],gfh=g_gfh.id,nconfig=idconf)
                    t_config.pacto = value
                    t_config.minimo = value
                    t_config.save()
                except Exception as e:
                    return HttpResponse('Hubo en fallo al actualizar, ' + str(e))
            g_conf = None
            g_gfh = None

            #disp = gfhs.objects.all()
            return render( request, 'actualizaPactos.html',{'hospital': hosp_update, }) #'dispositivo': disp
        
        else:
        
            #disp = gfhs.objects.filter(hp_id=hosp_update[0].id).select_related()
            
            #disp = gfhs.objects.all()
            print(request.META['REMOTE_ADDR'])
            print(request.META['HTTP_USER_AGENT'])
            print('Iniciando.')

            for key, value in request.POST.items():
                print('Key: ',str(key), '  Value: ', str(value))

            if request.method == 'POST':
                if request.POST.get('selHosp',True )  and request.POST.get('selGfh', True) and request.POST.get('selDisp', True):
                
                    d = request.POST['selDisp']
                    a = request.POST['selGfh']
                    h = request.POST['selHosp']
                    print('CHANGE',str(a))
                    
                    g_conf = excel.objects.filter(disp=dispositivos.objects.get(nombre=d), hosp=hospitales.objects.get(codigo=h)).select_related()
                    #print('Conf: ', conf)
                    g_gfh = g_conf[0].gfh
                    print('GFH_: ', g_gfh)
                    return render( request, 'actualizaPactos.html',{'hospital': hosp_update, 'pacto': g_conf, 'gfh': g_gfh}) #'dispositivo': disp,

    return render( request, 'actualizaPactos.html',{'hospital': hosp_update, }) #'dispositivo': disp


@transaction.atomic
def ActualizarPactos( request ):
    #disp = None
    global g_gfh
    global g_conf
    idconf = None
    hosp_update = hospitales.objects.all()
    if request.method == "POST":
        d = request.POST['selDisp']
        g = request.POST['selGfh']
        h = request.POST['selHosp']
        
        #print('Hospital: ',request.POST['selHosp']);'  Disp: ',request.POST['selDisp'];'  Gfh: ',request.POST['selGfh']
        if request.POST.get('selHosp', True)  and request.POST.get('selGfh', True) and request.POST.get('selDisp', True):
            clavesDescartar = ('csrfmiddlewaretoken', 'selHosp', 'selDisp', 'selGfh' ) #'oculto'
            dic = {}
            for key, value in request.POST.items():
                if key not in clavesDescartar:
                    if value != '':
                        print('VALOR : ' , str(key) + '  ',str(value))
                        dic[str(key)] = int(value)

            #print(dic)
            #print('GFH: ', g_gfh)
            for key, value in dic.items():
                try:
                    mtx = key.split('*')
                    print('VALUE: ', str(value))
                    GFH = gfhs.objects.get(gfh=g,nombre=d,hp_id=hospitales.objects.get(codigo=h).id)
                    HSP = hospitales.objects.get(codigo=h)
                    DSP = dispositivos.objects.get(nombre=d)

                    t_excel = excel.objects.get(modulo=mtx[1],estanteria=mtx[2],ubicacion=mtx[3],division=mtx[4],codigo=mtx[0],gfh=GFH)
                    t_excel.pacto = value
                    t_excel.minimo = value
                    t_excel.save()

                    idconf = funcConf.SetMaxId_gfh(GFH,DSP.id, HSP.id)
                    print('IDCONFIG: ', str(idconf))
                    t_config = configurations.objects.get(modulo=mtx[1],estanteria=mtx[2],ubicacion=mtx[3],division=mtx[4],codigo=mtx[0],gfh=gfhs.objects.get(gfh=g,nombre=d),nconfig=idconf)
                    t_config.pacto = value
                    t_config.minimo = value
                    t_config.save()
                except Exception as e:
                    return HttpResponse('Hubo en fallo al actualizar, ' + str(e))
            g_conf = None
            g_gfh = None

            #disp = gfhs.objects.all()
            return render( request, 'actualizaPactos.html',{'hospital': hosp_update, }) #'dispositivo': disp
        
        # else:
        
        #     #disp = gfhs.objects.filter(hp_id=hosp_update[0].id).select_related()
            
        #     #disp = gfhs.objects.all()
        #     print(request.META['REMOTE_ADDR'])
        #     print(request.META['HTTP_USER_AGENT'])
        #     print('Iniciando.')

        #     for key, value in request.POST.items():
        #         print('Key: ',str(key), '  Value: ', str(value))

        #     if request.method == 'POST':
        #         if request.POST.get('selHosp',True )  and request.POST.get('selGfh', True) and request.POST.get('selDisp', True):
                
        #             d = request.POST['selDisp']
        #             a = request.POST['selGfh']
        #             h = request.POST['selHosp']
        #             print('CHANGE',str(a))
                    
        #             g_conf = excel.objects.filter(disp=dispositivos.objects.get(nombre=d), hosp=hospitales.objects.get(codigo=h)).select_related()
        #             #print('Conf: ', conf)
        #             g_gfh = g_conf[0].gfh
        #             print('GFH_: ', g_gfh)
        #             return render( request, 'actualizaPactos.html',{'hospital': hosp_update, 'pacto': g_conf, 'gfh': g_gfh}) #'dispositivo': disp,

    return render( request, 'actualizaPactos.html',{'hospital': hosp_update, }) #'dispositivo': disp

def getConf(request):
    lista = []
    mtx = []
    bloque = """{"modulo": "","estanteria": "","ubicacion": "","division": "","codigo": "","nombre": "","pacto": ""  """
    
    if request.method == 'GET':
        #if request.POST['hospital'] and request.POST['ugs'] and request.POST['gfh']:
        hospital = request.GET['hospital']
        #gfh = request.GET['gfh']
        ugs = request.GET['ugs']
        h = hospitales.objects.get(codigo=hospital).pk
        d = dispositivos.objects.get(nombre=ugs).pk
        g = dispositivos.objects.get(nombre=ugs).gfh
        conf = excel.objects.filter(gfh=g,disp=d,hosp=h)
        #print('Cuantos: ', len(conf))
        f_json = Json(bloque)
        for i in conf:
            #print(str(i))
            mtx.append(i.modulo)
            mtx.append(i.estanteria)
            mtx.append(i.ubicacion)
            mtx.append(i.division)
            mtx.append(i.codigo)
            mtx.append(i.nombre.nombre)
            mtx.append(i.pacto)

            lista.append(mtx)
            mtx = []
        #print('Lista: ', str(lista))
        txtJson = f_json.crearJson(lista)
        #print(str(txtJson))
    return HttpResponse(txtJson)


def getHospital(request):
    #print(str(data))
    hospi = ''
    lista = []
    mtx = []
    bloque = """{"gfh": "","nombre": "" """

    if request.method == 'GET':
        hospi = request.GET['hospital']   
        hosp = hospitales.objects.get(codigo=hospi)
        gfh = gfhs.objects.filter(hp_id=hosp.id).select_related()
        f_json = Json(bloque)
        for i in gfh:
            mtx.append(i.gfh)
            mtx.append(i.nombre)
            lista.append(mtx)
            mtx = []
        #print('Lista: ', lista)
        txtJson = f_json.crearJson(lista)

    #print('JSON: ' + txtJson)
    return HttpResponse(txtJson)


def getUgs( request ):
    ugs = ''
    lista = []
    mtx = []
    bloque = """{"gfh": "","ugs": "" """
    if request.method == 'GET':
        ugs = request.GET['ugs']
        hospi = request.GET['hospital']
        #print('Hospital: ', hospi, '  UGS: ', ugs)
        hosp = hospitales.objects.get(codigo=hospi)
        ugs = gfhs.objects.filter(hp_id=hosp.id,gfh=ugs).select_related()
        #print(ugs)
        f_json = Json(bloque)
        for i in ugs:
            mtx.append(i.gfh)
            mtx.append(i.nombre)
            lista.append(mtx)
            mtx = []

        txtJson = f_json.crearJson(lista)
        return HttpResponse(txtJson)
    