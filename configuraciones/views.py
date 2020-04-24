#import os
from django.http import HttpResponseRedirect
from django.template import Template 
from django.shortcuts import render
from django.http import HttpResponse , Http404
from configuraciones.models import  articulos , configurations , gfhs , dispositivos, hospitales
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm
from os import remove , listdir
from configuraciones.excell import Excell
from configuraciones.excell import comprobarExcel
from HtmlHack.settings import MEDIA_ROOT
from HtmlHack.settings import STATIC_ROOT
from django.db import connection, transaction
from django.db.models import Q
#from configuraciones.qrcode import generate
#from configuraciones.qrcode import make
import qrcode

#from somewhere import handle_uploaded_file
# Create your views here.

def config1( request ):
    contexto = { 'titulo': 'Configuraciones', 'dato': 'ESTA ES UNA NUEVA CONFIGURACION.'}
    return render( request ,'ini.html', contexto )


def upload_file(request):
    if request.method == 'POST' and request.FILES['upload']:
        fichero = request.FILES['upload']
        #print( fichero.name )
        #print( fichero.size )
        #print(fichero.content_type)
        fs = FileSystemStorage()
        filename = fs.save( fichero.name , fichero  )
        file_url = fs.url( filename )
        nfilas = ''
        if '.xlsx' in fichero.name:
            print('FICHERO EXCEL DETECTADO: ', fichero.name )
            #Llamar a funcion para hacer cambio de configuracion.
            excel = Excell( MEDIA_ROOT +'/' + fichero.name )
            nfilas = str( excel.getnumerofilas() -1 )
            #print( 'Numero de columnas: ' + str( excel.getnumerocolumnas() ))
            fila = excel.leer_fichero()

            #_______________________COMPROBAR EXCEL______________________________________
            columnas = ''; vacios = [] ; duplicados = []; gfhdisp = []
            comprobar = comprobarExcel( fila )

            columnas = excel.getnumerocolumnas()

            v = comprobar.comprobarVacios()
            if len( v ) > 1:
                vacios = v

            dup = comprobar.comprobarDuplicados( ) 
            if len( dup ) > 0:
                duplicados = dup

            gfh = comprobar.comprobarGfhDisp()
            if len( gfh ) > 0:
                gfhdisp = gfh

            if columnas != 12 or len( vacios ) > 0 or len( duplicados ) > 0 or len( gfh ) > 0:
                print('Columnas: ' + str(columnas) + '  Vacios: '+ str( vacios) + '  Duplicados: '+str(duplicados) + '  GfhD: '+ str(gfhdisp))
                remove( MEDIA_ROOT +'/' + fichero.name )
                return render( request, 'error.html', {'columnas': columnas, 'vacios': vacios, 'duplicados': duplicados ,'gfh': gfhdisp,}) 

            #____________________________________________________________________________
            rmgfh = fila[0]
            print('Dispositivo: ' + str( rmgfh[10] ) )
            #____________________________________SQL_____________________________________
            cursor = connection.cursor()
            rmv = cursor.execute('SELECT id , gfh_id FROM configuraciones_dispositivos WHERE nombre = %s',[ rmgfh[10] ])
            try:
                rmv = rmv.fetchall()[0]
            except Exception as e:

                rmv = rmv.fetchone() #Si pasa por aqui es porque ese equipo no existe
                #return HttpResponse('ERROR: Nombre de dispositivo o GFH mal indicado en excel.' + str( e ) + ' '+ str( rmv ) )
                return render( request, 'error.html', { 'except': str( e ) + '   ' + str( rmv ) })
            borradas = configurations.objects.filter( gfh=rmv[1], disp=rmv[0] ).delete()
            cursor = None
            indice = 1
            #____________________________________________________________________________
            for i in fila:
                try:
                    #_________________________MODO SQL____________________________________
                    cursor = connection.cursor()
                    try:
                        cursor.execute('SELECT id FROM configuraciones_hospitales WHERE codigo = %s',[ i[11] ] )
                        i[11] = cursor.fetchone()[0]
                        cursor.execute( 'SELECT idsel FROM configuraciones_articulos WHERE codigo = %s',[ i[4] ] )
                        i[5] = cursor.fetchone()[0] #AQUI esta la pk del articulo.
                        #print('Articulo' + str(i[5]))
                    except:
                        #artnew = articulos(codigo=i[4] ,nombre=i[5] ,hospital=i[11])
                        #artnew.save()
                        consulta = "INSERT INTO configuraciones_articulos(codigo,nombre,hospital_id)VALUES\
                        ('"+str(i[4])+"','"+str(i[5])+"','"+str(i[11])+"')"
                        cursor.execute( consulta )
                        consulta = 'SELECT idsel FROM configuraciones_articulos WHERE codigo = %s',[ i[4] ]
                        cursor.execute( consulta )
                        i[5] = cursor.fetchone()[0]
                        #print('Articulo_Nuevo: ' + str( i[5] ))
                    
                    cursor.execute('SELECT id FROM configuraciones_gfhs WHERE gfh = %s',[i[9] ])
                    i[9] = str(cursor.fetchone()[0])
                    #print('pk_Gfh: ' + str(i[9]))
                    cursor.execute('SELECT id FROM configuraciones_dispositivos WHERE nombre = %s',[ str(i[10]) ] )
                    i[10] = str(cursor.fetchone()[0])
                    #print('pk_Disp: ' + str(i[10]))
                    #cursor.execute('SELECT id FROM configuraciones_hospitales WHERE codigo = %s',[ i[11] ] )
                    #i[11] = cursor.fetchone()[0]
                    #print( 'GFH2: '+ str( i[9]) + ' DISP2: ' + str( i[10] ))
                    #cursor = None
                    #_____________________________________________________________________
                    #print('REEMPLAZANDO: ' + str(i[6]) + ' '+ str(i[7]) )
                    i[6] = str.replace( str(i[6]), ',','.' )  #cambiar coma por punto.
                    i[7] = str.replace( str(i[7]), ',','.' )

                    if i[9] == rmgfh[9]:
                        #cursor = connection.cursor()
                        #data = configurations( modulo=i[0],estanteria=i[1],ubicacion=i[2],division=i[3],codigo=i[4],
                        #nombre_id= i[5], pacto=float( str(i[6]) ), minimo=float( str(i[7]) ),dc=i[8],gfh=i[9],disp=i[10],hosp=i[11] )
                        #data.save()
                        consulta = "INSERT INTO configuraciones_configurations(modulo,estanteria,ubicacion,division,codigo,nombre_id,pacto,minimo,dc,gfh,disp,hosp_id)"\
                        "VALUES('"+str(i[0])+"','"+str(i[1])+"','"+str(i[2])+"','"+str(i[3])+"','"+str(i[4])+"','"+str(i[5])+"',\
                        '"+str(i[6])+"','"+str(i[7])+"','"+str(i[8])+"','"+str(i[9])+"','"+str(i[10])+"','"+str(i[11])+"')"
                        #print( consulta )
                        cursor.execute( consulta )
                        indice += 1
                    else:
                        cursor = None
                        return render(request, 'SubirConfig.html', { 'borradas': borradas[0], 'nfilas': nfilas })
                except Exception as e:
                    file_url = 'Hubo un fallo al subir configuracion. ' + str( e ) + ' En linea ' + str(indice)
                    remove( MEDIA_ROOT +'/' + fichero.name )
                    return HttpResponse( file_url)
                    
        remove( MEDIA_ROOT +'/' + fichero.name )
        return render(request, 'SubirConfig.html', {'uploaded_file': file_url , 'borradas': borradas[0], 'nfilas': nfilas })
    #else:
        #form = UploadFileForm()
    return render(request, 'SubirConfig.html') #, {'form': form})


def download_file(request):
    retorno = []
    nlineas = ''
    res = ''
    gfhId = ''
    gfhNombre = ''
    #dispNombre = []
    dispIds = []
    dispId = ''
    dispositivo = ''
    hospitalP = ''
    code = ''
    cqr = ''
    cqrlist = {}
    if  request.method == 'POST':
        if request.POST['gfh']:
            gfhNombre = request.POST['gfh']
        if request.POST['disp']:
            dispositivo = request.POST['disp']
        if request.POST['code']:
            code = request.POST['code']
        #ubic = request.POST['ubic']

        #__________________________________SQL___________________________________________
        try:
            cursor = connection.cursor()
            
            if dispositivo:
                cursor.execute('SELECT gfh_id FROM configuraciones_dispositivos WHERE nombre = %s ', [ dispositivo ])
                gfhId = cursor.fetchone()[0]
                print('GFH_id: '+str(gfhId))
                cursor.execute('SELECT gfh FROM configuraciones_gfhs WHERE id = %s ', [ gfhId ])
                gfhNombre = cursor.fetchone()[0]
                print('GFH_nombre: '+str(gfhNombre))
                cursor.execute('SELECT id FROM configuraciones_dispositivos WHERE nombre = %s', [ dispositivo ])
                dispId = cursor.fetchone()[0]
                print('IdDisp:'+str(dispId))

            if gfhNombre:
                cursor.execute('SELECT id FROM configuraciones_gfhs WHERE gfh = %s ', [ gfhNombre ])
                gfhId = cursor.fetchone()[0]  #Aqui tenemos el ID del gfh en una lista de un item 
                print( 'gfh_id2: '+ str(gfhId))
                cursor.execute('SELECT id FROM configuraciones_dispositivos WHERE gfh_id = %s', [ gfhId ])
                #dispIds.clear()
                dtmp = cursor.fetchall()
                print('dispId: '+str(dtmp))
                
                for i in dtmp: #Aqui tenemos una lista con los IDS de los dispositivos del gfh.
                    dispIds.append( str(i[0]))
                    print( 'ids: ' + str(dispIds[-1]))
                cursor.execute('SELECT nombre FROM configuraciones_dispositivos WHERE gfh_id = %s', [ gfhId ])
                dtmp = cursor.fetchall()[0]
                print('dispNombre: '+str(dtmp))
                cursor.execute('SELECT gfh_id from configuraciones_dispositivos WHERE nombre = %s',[dtmp[0]])
                gfhId = cursor.fetchone()[0]
                print(dtmp[0])
                print('GFH-ID: '+ str(gfhId))

            #     print( 'id: ' + str(dispNombre[-1])+ ' IndiceDispositivo: '+ str(indDisp))
            if code and not dispositivo and not gfhNombre:
                print('Entro en code  ' + str(code) )
                res = configurations.objects.filter( codigo=code).order_by('gfh','modulo','estanteria','ubicacion')
            elif dispositivo and code:
                print('Entro en dispositivo and code  ' + str(dispId) + ' '+code )
                res = configurations.objects.filter( disp=dispId, codigo=code ).order_by('modulo','estanteria','ubicacion')
            elif gfhNombre and code:
                print('Entro en gfhNombre and code  ' + gfhNombre + ' ' + code )
                res = configurations.objects.filter( gfh=gfhId , codigo=code ).order_by('modulo','estanteria','ubicacion')
            elif dispositivo:
                print('Entro en dispositivo  ' + str(dispId) )
                res = configurations.objects.filter( disp=dispId).order_by('modulo','estanteria','ubicacion')
            elif gfhNombre:
                print('Entro en gfhNombre  ' + gfhNombre + '  '+str(gfhId) )
                res = configurations.objects.filter( gfh=gfhId).order_by('disp','modulo','estanteria','ubicacion')
                
            cursor = None
        except Exception as e:
            print('Excepcion en la consulta.' + str( e ))
            
        #print('GFH: ' + str( gfhP ) + ' DISPOSITIVO:' + str( dispP[0] ) + ' HOSPITAL: ' + hospitalP)
        #gfh = 'GFH: ' + str( gfhNombre )
        nlineas = 'NUMERO DE LINEAS: ' + str( len(res))
        print('NUMERO DE LINEAS: ' + str( len(res)))
        print(str(res))
        excel = Excell( 'data' )

        ultimaFila = 2
        for i in res:
            #______________________________MODO SQL___________________________________
            cursor = connection.cursor()
            cursor.execute( 'SELECT nombre FROM configuraciones_articulos WHERE configuraciones_articulos.idsel = %s', [i.nombre_id] )
            articulos = cursor.fetchall()[0][0]
            cursor.execute('SELECT nombre FROM configuraciones_dispositivos WHERE id = %s', [i.disp])
            dispositivo = cursor.fetchone()[0]
            cursor.execute('SELECT gfh FROM configuraciones_gfhs WHERE id = %s', [i.gfh])
            print('ID_Config: '+ str(i.gfh))
            gfhNombre = cursor.fetchone()[0]
            cursor.execute('SELECT codigo FROM configuraciones_hospitales WHERE id = %s', [i.hosp_id])
            hospitalP = cursor.fetchone()[0]

            cursor = None
            cqr = str(i.modulo)+'-'+str(i.estanteria)+'-'+str(i.ubicacion)+'-'+str(i.division)+' '+str(i.codigo)+' '+str(articulos)+\
            ' '+str(i.pacto)+' '+str(i.minimo)+' '+str(i.dc)+' '+str(gfhNombre)+' '+str(dispositivo)+' '+str(hospitalP )
            cqrlist.update({ i.codigo : cqr })
            #_________________________________________________________________________
            ret = []
            ret.append(i.modulo)
            ret.append(i.estanteria)
            ret.append(i.ubicacion )
            ret.append(i.division )
            ret.append(i.codigo )
            ret.append( articulos ) #i.nombre_id
            ret.append(i.pacto )
            ret.append(i.minimo )
            ret.append(i.dc )
            ret.append( gfhNombre )
            ret.append( dispositivo )
            ret.append( hospitalP )
            ret.append( cqr )
            retorno.append( ret )
# ____________FASE LLENAR EXCEL____________________
            excel.insertar_rangofila( ret , ultimaFila , 1 )
            ultimaFila += 1
            ret = None
        ret = ['modulo','estanteria','ubicacion','division','codigo',
        'nombre','pacto','minimo','dc','gfh','disp','hosp_id']
        excel.insertar_rangofila( ret , 1 , 1 )
        excel.salvarexcell2()
        #excel.cambiarcolorfila(1 ,1 ,'yellow','yellow')
# ____________END FASE LLENAR EXCEL________________
# ____________FASE DOWNLOAD FILA____________________        
        #print( excel.nombre )
        fila = MEDIA_ROOT +'/' + 'data.xlsx'
        print('FilaExcel: '+ fila)
        if 'bajarfila' in request.POST:
            import os
            with open( fila , 'rb') as fh:
                #print('ENTRO')
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename( fila )
                remove( fila )
                return response
        try:
            remove( fila )  #eliminamos fichero del servidor.
        except Exception as e:
            print('No existe fichero '+ str(e) )
# ____________END FASE DOWNLOAD FILA____________________
    return render(request, 'BajarConfig.html', {'configuraciones': retorno,
    'nombre': gfhNombre, 'lineas': nlineas , 'cqr': cqrlist })


def articulosAdd(request):
    #print( MEDIA_ROOT +'/' + 'articulos.xlsx' )
    excel = None
    excel = Excell( MEDIA_ROOT +'/' + 'articulos.xlsx' )# , 'Hoja1')
    nfilas = str( excel.getnumerofilas() -1 )
    fila = excel.leer_fichero()
    print( 'Numero de lineas: ' + str( nfilas) )
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
    print( 'Numero de lineas: ' + str( nfilas) )
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
    print( 'Numero de lineas: ' + str( nfilas) )
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


def addFotoArticulo( rutaNombreFichero , codigo ):
    #consulta = 'UPDATE configuraciones_articulos set foto = %s WHERE codigo = %s ',[ rutaNombreFichero , codigo ]
    #print( consulta )
    #cursor = connection.cursor()
   # res = ''
    try:
        #cursor.execute( consulta )
        #print ('Codigo ' + codigo +' añadido correctamente.')
        #cursor = None
        p = articulos.objects.filter(codigo=codigo, hospital_id=2 ).update(foto=rutaNombreFichero)
        #print(str(p))
        #p.save()
        return '0'
    except Exception as e:
        #print('Fallo al insertar foto en el codigo ' + str(codigo))
        res = 'Fallo al actualizar: ' + str( e ) + ' Codigo: '+codigo+' Ruta: '+rutaNombreFichero
        #cursor = None
    return str( res )


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
        print('res: '+res )
        if res == '0':
            #return HttpResponse( 'Ruta fotos añadida correctamente' )
            print('Codigo '+codigo+' añadido correctamente')
    return HttpResponse( res)
    
def verArticulo( request ):
    #img = '010181.png' 
    #image_data = open( MEDIA_ROOT + "/articulos/" + img , "rb").read()
    #return HttpResponse(image_data, content_type="image/png")
    img = None
    if request.method == 'POST' and request.POST['verimg']:
        codigo = request.POST['verimg']
        img = articulos.objects.filter(codigo= codigo)[0]
        print( str(img))
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
        print('Numero de registros: ' + str(len(img)))
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
        imagen = open('media/qrcode.png','wb')
        img.save(imagen)
        imagen.close()
        imagen = open('media/qrcode.png','rb').read()
        return HttpResponse( imagen, content_type="image/png")

    return render( request , 'galeria.html',{'imagen': img })
    
def mostrarCodigoGRpng( request ):
    if request.method == 'POST' and request.POST['verimg']:
        valor = request.POST['verimg']
        img = qrcode.make( valor )
        imagen = open('media/qrcode.png','wb')
        img.save(imagen)
        imagen.close()
        return render( request , 'galeria.html',{'qrcode': 'media/qrcode.png' })
    return render( request , 'galeria.html')

def verCgr( request ):
    #items = request.META.items()
    items = request.GET['data']
    fila = items.split(' ')
    codigo = fila[1]
    foto = articulos.objects.filter(codigo=codigo) #.values('foto')[0]
   
    print('RUTA: ' + str(foto))
    img = qrcode.make( items )
    imagen = open('media/qrcode.png','wb')
    img.save( imagen )
    imagen.close()
    return render( request , 'cqr.html',{'cqr': items , 'qrcode': 'media/qrcode.png','img': foto ,} )





    


