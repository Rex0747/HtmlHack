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
import glob


#from somewhere import handle_uploaded_file
# Create your views here.

def config1( request ):
    contexto = { 'titulo': 'Configuraciones', 'dato': 'ESTA ES UNA NUEVA CONFIGURACION.'}
    return render( request ,'ini.html', contexto )


def upload_file(request):
    if request.method == 'POST' and request.FILES['upload']:
        fichero = request.FILES['upload']
        #print( str(fichero ))
        #print( fichero.name )
        #print( fichero.size )
        #print(fichero.content_type)

        rta = glob.glob(MEDIA_ROOT+'/*.xlsx')
        for f in rta:
            remove(f)

        fs = FileSystemStorage()
        filename = fs.save( fichero.name , fichero  )
        file_url = fs.url( filename )
        nfilas = ''
        if '.xlsx' in fichero.name:
            #print('FICHERO EXCEL DETECTADO: ', fichero.name )
            #Llamar a funcion para hacer cambio de configuracion.
            excel = Excell( MEDIA_ROOT +'/' + fichero.name )
            nfilas = str( excel.getnumerofilas() -1 )
            #print( 'Numero de columnas: ' + str( excel.getnumerocolumnas() ))
            fila = excel.leer_fichero()

            #_______________________COMPROBAR EXCEL______________________________________
            columnas = ''; vacios = [] ; duplicados = []; gfhdisp = []
            comprobar = comprobarExcel( fila )

            columnas = excel.getnumerocolumnas()
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

            if (columnas != 12) and (len( vacios ) > 0) and (len( duplicados ) > 0) and (len( gfh ) > 0):
                #print('Columnas: ' + str(columnas) + '  Vacios: '+ str( vacios) + '  Duplicados: '+str(duplicados) + '  GfhD: '+ str(gfhdisp))
                remove( MEDIA_ROOT +'/' + fichero.name )
                return render( request, 'error.html', {'columnas': columnas, 'vacios': vacios, 'duplicados': duplicados ,'gfh': gfhdisp,}) 

            #____________________________________________________________________________
            rmgfh = fila[0]
            #print('Dispositivo: ' + str( rmgfh[10] ) )
            #____________________________________SQL_____________________________________
            cursor = connection.cursor()
            rmv = cursor.execute('SELECT id , gfh_id FROM configuraciones_dispositivos WHERE nombre = %s',[ rmgfh[10] ])
            try:
                rmv = rmv.fetchall()[0]
                borradas = configurations.objects.filter( gfh=rmv[1], disp=rmv[0] ).delete()
                print('Borradas: '+str(borradas) , ' gfh: '+str(rmv[1]), ' disp: '+str(rmv[0]))
                print(str(rmv))

            except Exception as e:
                rmv = rmv.fetchone() #Si pasa por aqui es porque ese equipo no existe
                #return HttpResponse('ERROR: Nombre de dispositivo o GFH mal indicado en excel.' + str( e ) + ' '+ str( rmv ) )
                return render( request, 'error.html', { 'except': str( e ) + '   ' + str( rmv ) })
            
            #borradas = cursor.execute('DELETE FROM configuraciones_configurations WHERE gfh=%s and disp=%s',[rmv[1], rmv[0]])
            
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
                        consulta = "INSERT INTO configuraciones_articulos(codigo,nombre,hospital_id,foto)VALUES\
                        ('"+str(i[4])+"','"+str(i[5])+"','"+str(i[11])+"','"+str('articulos/'+str(i[4])+'.png')+"')"
                        cursor.execute( consulta )
                        #print('Articulo_Nuevo: ' + str( i[5] ))
                        cursor.execute( 'SELECT idsel FROM configuraciones_articulos WHERE codigo = %s',[ i[4] ] )
                        i[5] = cursor.fetchone()[0]
                        
                    cursor.execute('SELECT gfh_id FROM configuraciones_dispositivos WHERE nombre = %s',[i[10] ])
                    #cursor.execute('SELECT id FROM configuraciones_gfhs WHERE gfh = %s',[i[9] ])
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
    articulo = None
    dispId = ''
    dispositivo = ''
    hospital = ''
    code = ''
    cqr = ''
    global gfhdispdown

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
            hospital_id = getIdDB( hospitales.objects.filter(codigo=hospital),'id' )
            #___________________________________
            
            if dispositivo:
                gfhId = getIdDB(dispositivos.objects.filter( nombre =dispositivo) , 'gfh_id')
                #print('GFH_id: '+str(gfhId))

                gfhNombre = getIdDB(gfhs.objects.filter(id=gfhId), 'gfh')
                #print('GFH_nombre: '+str(gfhNombre))

                dispId = getIdDB( dispositivos.objects.filter(nombre=dispositivo), 'id')
                #print('IdDisp:'+str(dispId))

            if gfhNombre:
                gfhId = getIdDB(gfhs.objects.filter(gfh=gfhNombre), 'id')
                #print( 'gfh_id3: '+ str(gfhId))
                dtmp = getIdDB(dispositivos.objects.filter(gfh=gfhId), 'nombre')
                #print('dispNombre: '+str(dtmp))
                gfhId = getIdDB(dispositivos.objects.filter(nombre=dtmp),'gfh_id')
                #print('gfh_id4: '+ str(gfhId))
                #_________________________numero de mismo codigo en DB_____________________________
            
                #__________________________________________________________________________________
            if code and not dispositivo and not gfhNombre:
                #print('Entro en code  ' + str(code) )
                res = configurations.objects.filter(  codigo=code ,hosp=hospital_id ).order_by('gfh','modulo','estanteria','ubicacion')
                #print('codigo: '+ str(code))
                #print('hospital: '+ str(hospital_id))
            elif dispositivo and code:
                #print('Entro en dispositivo and code  ' + str(dispId) + ' '+code )
                res = configurations.objects.filter( disp=dispId, codigo=code ,hosp=hospital_id ).order_by('modulo','estanteria','ubicacion')
            elif gfhNombre and code:
                #print('Entro en gfhNombre and code  ' + gfhNombre + ' ' + code )
                res = configurations.objects.filter( gfh=gfhId , codigo=code ,hosp=hospital_id ).order_by('modulo','estanteria','ubicacion')
            elif dispositivo:
                #print('Entro en dispositivo  ' + str(dispId) )
                res = configurations.objects.filter( disp=dispId ,hosp=hospital_id ).order_by('modulo','estanteria','ubicacion')
            elif gfhNombre:
                #print('Entro en gfhNombre  ' + gfhNombre + '  '+str(gfhId) )
                res = configurations.objects.filter( gfh=gfhId ,hosp=hospital_id).order_by('disp','modulo','estanteria','ubicacion')  
            
        except Exception as e:
            print('Excepcion en fase 1.' + str( e ))
            
        nlineas = 'NUMERO DE LINEAS: ' + str( len(res))
        print('NUMERO DE LINEAS: ' + str( len(res)))
        #print('RES: '+str(res))
        excel = Excell( dispdown ) #Excell( 'data' )
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
                

            dispositivo = getIdDB(dispositivos.objects.filter(id=i.disp), 'nombre')
            gfhNombre = getIdDB(gfhs.objects.filter(id=i.gfh), 'gfh')
            cursor = None
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
            excel.insertar_rangofila( ret , ultimaFila , 1 )
            ultimaFila += 1
            ret = None
        #print('Retorno: ' + str(retorno))
        ret = ['modulo','estanteria','ubicacion','division','codigo',
        'nombre','pacto','minimo','dc','gfh','disp','hosp_id']
        excel.insertar_rangofila( ret , 1 , 1 )
        excel.salvarexcell2()
        #excel.cambiarcolorfila(1 ,1 ,'yellow','yellow')
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
    return render(request, 'BajarConfig.html', {'configuraciones': retorno,
    'nombre': gfhNombre, 'lineas': nlineas , 'cqr': cqrlist })


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


def addFotoArticulo( rutaNombreFichero , codigo ):

    try:
        p = articulos.objects.filter(codigo=codigo, hospital_id=2 ).update(foto=rutaNombreFichero)
        return '0'
    except Exception as e:
        res = 'Fallo al actualizar: ' + str( e ) + ' Codigo: '+codigo+' Ruta: '+rutaNombreFichero
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




def getIdDB( formula, campo ):
    d = formula
    #print(str(d) + ' len: ' +str(len(d)))
    if len(d)==1:
        return d.values(campo)[0].get(campo)
    if len(d)>1:
        return d.values(campo)[0].get(campo)
