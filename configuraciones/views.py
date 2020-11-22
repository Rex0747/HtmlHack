#import os
from django.http import HttpResponseRedirect
from django.template import Template 
from django.shortcuts import render
from django.http import HttpResponse , Http404
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



#from somewhere import handle_uploaded_file
# Create your views here.

def config1( request ):
    contexto = { 'titulo': 'Configuraciones', 'dato': 'ESTA ES UNA NUEVA CONFIGURACION.'}
    return render( request ,'ini.html', contexto )

def upload_fileNewDeprecated(request):
    if request.method == 'POST' and request.FILES['upload']:
        fichero = request.FILES['upload']
        rta = glob.glob(MEDIA_ROOT+'/*.xlsx')
        for f in rta:
            remove(f)
        
        fs = FileSystemStorage()
        filename = fs.save( fichero.name , fichero  )
        file_url = fs.url( filename )
        nfilas = ''
        Carticulos = articulos.objects.all()   #instancia de articulos
        #print('Carticulos: ', str(Carticulos))

        if '.xlsx' in fichero.name:
            excel1 = Excell( MEDIA_ROOT +'/' + fichero.name )
            nfilas = str( excel1.getnumerofilas() -1 )
            listaExcel = excel1.leer_fichero2() #lista leida por el excel
            print('ListaExcel: ' + str(listaExcel))
            try:
                disp = dispositivos.objects.filter( nombre=listaExcel[0].dispositivo)[0] # objeto dispositivo
                gfh = gfhs.objects.filter( nombre=disp.nombre) # objeto gfh
                hosp_id = getIdDB( hospitales.objects.filter(codigo=listaExcel[0].hospital),'id')
                listaDb = configurations.objects.filter( gfh=disp.gfh_id , disp=disp.id , hosp_id=hosp_id ).select_related('nombre','hosp','gfh','disp')\
                .only('modulo','estanteria','ubicacion','division','codigo','nombre','pacto','minimo','dc','gfh','disp','hosp')
                    
            except Exception as e:
                return HttpResponse('No esta configurado el gfh '+str(listaExcel[0].gfh))
            sesion = GetAleatorio()

            for itm in listaExcel:
                try:
                    a = None
                    d = dispositivos.objects.get(nombre=itm.dispositivo)
                    h = hospitales.objects.get(codigo=itm.hospital)
                    g = gfhs.objects.get(gfh=itm.gfh, nombre=itm.dispositivo)
                    if articulos.objects.filter(codigo=itm.codigo).exists():
                        a = articulos.objects.get(codigo=itm.codigo, hospital=h)
                    else:
                        a = articulos(codigo=itm.codigo, nombre=itm.nombre, hospital=h, foto=itm.codigo+'.png')
                        a.save()
                    conf = excel(modulo=itm.modulo,estanteria=itm.estanteria,ubicacion=itm.ubicacion,division=itm.division,\
                    codigo=itm.codigo,nombre=a,pacto=itm.pacto,minimo=itm.minimo,dc=itm.dc,gfh=g,disp=d,hosp=h,sesion=sesion)
                    conf.save()
                    print('Inserto filas y tal vez articulos en tabla excel')
                except Exception as e:
                    print('Error ' + str(e))
                    excel.objects.filter(sesion=sesion).delete()
                    return HttpResponse('Fallo al insertar tabla excell. '+ str(e))

            listaXlsx = excel.objects.filter( gfh=disp.gfh_id , disp=disp.id , hosp_id=hosp_id ).select_related('nombre','hosp','gfh','disp')\
                .only('modulo','estanteria','ubicacion','division','codigo','nombre','pacto','minimo','dc','gfh','disp','hosp')
            print(listaXlsx)
            print('___________________________________________________________________')
            print(listaDb)
            print('___________________________________________________________________')
            #qs1 = excel.objects.none()
            qsUnion = listaXlsx.union(listaDb, all=False).values_list('modulo','estanteria','ubicacion','division','codigo','pacto','gfh_id','disp_id','hosp_id')
            #qsUnion = listaXlsx.all().union(listaDb, all=False).values_list('modulo','estanteria','ubicacion','division','codigo','gfh_id','disp_id','hosp_id')
            print('UNION: ' + str(qsUnion))
            print('___________________________________________________________________')
            qsDiff = listaXlsx.difference(listaDb).values_list('modulo','estanteria','ubicacion','division','codigo','pacto','gfh_id','disp_id','hosp_id')
            #qsDiff = listaXlsx.all().difference(listaDb, all=False).values_list('modulo','estanteria','ubicacion','division','codigo','gfh_id','disp_id','hosp_id')
            print('Diferencia: '+ str(qsDiff))
            print('___________________________________________________________________')
            qsInter = listaXlsx.intersection(listaDb).values_list('modulo','estanteria','ubicacion','division','codigo','pacto','gfh_id','disp_id','hosp_id')
            #qsInter = listaXlsx.all().intersection(listaDb, all=False).values_list('modulo','estanteria','ubicacion','division','codigo','gfh_id','disp_id','hosp_id')
            print('Interseccion: '+ str(qsInter))
            print('___________________________UNION___________________________________')
            UNION = concatQS(qsUnion)
            DIFER = concatQS(qsDiff)
            INTER = concatQS(qsInter)
            print(str(UNION))
            print('____________________________DIFFERENCIA__________________________________')
            print(str(DIFER))
            print('____________________________INTERSECCION__________________________________')
            print(str(INTER))



            
            conf = configurations.objects.filter( gfh=disp.gfh_id , disp=disp.id , hosp_id=hosp_id )
            print('CuantosDB: ', conf.count())
            print('CuantosEx: ', len(listaExcel))
            j = 0
            for i in listaExcel:
                try:
                    a = None
                    d = dispositivos.objects.get(nombre=i.dispositivo)
                    h = hospitales.objects.get(codigo=i.hospital)
                    g = gfhs.objects.get(gfh=i.gfh, nombre=i.dispositivo)
                    #print('gfh: ', str(g))
                    try:
                        if listaDb.filter(codigo=i.codigo).exists():
                            a = articulos.objects.get(codigo=i.codigo, hospital=h)
                            #dup = configurations.objects.filter( codigo=i.codigo, gfh=disp.gfh_id , disp=disp.id , hosp_id=hosp_id )
                            
                            configurations.objects.filter(codigo=i.codigo,  gfh=disp.gfh_id , disp=disp.id , hosp_id=hosp_id ).update(modulo=i.modulo,\
                                estanteria=i.estanteria,ubicacion=i.ubicacion,division=i.division,codigo=i.codigo,nombre=a,\
                                pacto=i.pacto,minimo=i.minimo)

                        else:
                            #a = articulos(codigo=i.codigo, nombre=i.nombre, hospital=h, foto=i.codigo+'.png')
                            #a.save()
                            a = articulos.objects.get(codigo=i.codigo, hospital=h)
                            conf = configurations(modulo=i.modulo,estanteria=i.estanteria,ubicacion=i.ubicacion,division=i.division,\
                            codigo=i.codigo,nombre=a,pacto=i.pacto,minimo=i.minimo,dc=i.dc,\
                            gfh=g,disp=d,hosp=h)
                            conf.save()
                            print('Inserto articulos y filas.')

                        
                        j += 1
                    except Exception as e:
                        print('Hubo un fallo.', str(e))
                        # a = articulos(codigo=i.codigo, nombre=i.nombre, hospital=h, foto=i.codigo+'.png')
                        # a.save()
                        # a = articulos.objects.get(codigo=i.codigo, hospital=h)
                        # print('articulo: ',str(a))
                        # conf = configurations(modulo=i.modulo,estanteria=i.estanteria,ubicacion=i.ubicacion,division=i.division,\
                        #     codigo=i.codigo,nombre=a,pacto=i.pacto,minimo=i.minimo,dc=i.dc,\
                        #     gfh=g,disp=d,hosp=h)
                        # conf.save()

                
                except Exception as e:
                    print('Excepcion: ', str(e))
                    #print('Clase articulos: ', str(a))

            excel.objects.filter(sesion=sesion).delete()

    return render(request, 'SubirConfig.html')

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
            #print('ListaExcel: ' + str(listaExcel))
            try:
                dispo = dispositivos.objects.filter( nombre=listaExcel[0].dispositivo)[0] # objeto dispositivo
                gfh = gfhs.objects.filter( nombre=dispo.nombre)[0] # objeto gfh
                hosp_id = getIdDB( hospitales.objects.filter(codigo=listaExcel[0].hospital),'id')
                # listaDb = configurations.objects.filter( gfh=disp.gfh_id , disp=disp.id , hosp_id=hosp_id ).select_related('nombre','hosp','gfh','disp')\
                # .only('modulo','estanteria','ubicacion','division','codigo','nombre','pacto','minimo','dc','gfh','disp','hosp')
                    
            except Exception as e:
                return HttpResponse('No esta configurado el gfh '+str(listaExcel[0].gfh))

            idconfig = GetAleatorio() #mejorar para evitar colision.

                #max_rated_entry = YourModel.objects.latest('rating')
                #return max_rated_entry.details

            borradas = configurations.objects.filter( gfh=gfh.id, disp=dispo.id ).delete()[0]
            #A la espera de implantar historico de configuraciones.
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
                except Exception as e:
                    print('Hubo un fallo.', str(e))

    return render(request, 'SubirConfig.html', {'uploaded_file': file_url , 'borradas': borradas, 'nfilas': nfilas })

def upload_fileMal(request):
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
            #region COMPROBAR EXCEL
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

            if (columnas != 11) and (len( vacios ) > 0) and (len( duplicados ) > 0) and (len( gfh ) > 0):
                #print('Columnas: ' + str(columnas) + '  Vacios: '+ str( vacios) + '  Duplicados: '+str(duplicados) + '  GfhD: '+ str(gfhdisp))
                remove( MEDIA_ROOT +'/' + fichero.name )
                return render( request, 'error.html', {'columnas': columnas, 'vacios': vacios, 'duplicados': duplicados ,'gfh': gfhdisp,}) 
            #endregion
            #____________________________________________________________________________
            rmgfh = fila[0]
            #print('Dispositivo: ' + str( rmgfh[10] ) )
            #____________________________________SQL_____________________________________
            rmv=None
            try:
                rmv = dispositivos.objects.filter( nombre=rmgfh[10])[0]#.get('id').get('gfh_id')
                print( str(rmv.id) + '  ' + str(rmv.gfh_id))
                borradas = configurations.objects.filter( gfh=rmv.gfh_id, disp=rmv.id ).delete()

            except Exception as e:
                #rmv = rmv.fetchone() #Si pasa por aqui es porque ese equipo no existe
                return render( request, 'error.html', { 'except': str( e ) + '   ' + str( rmv ) })
            
            cursor = None
            indice = 1
            #print(str(fila))
            #____________________________________________________________________________
            for i in fila:
                try:
                    #_________________________MODO SQL____________________________________
                    cursor = connection.cursor()
                    
                    try:
                        codHosp = i[11]
                        i[11] = hospitales.objects.filter(codigo=i[11])[0]
                        
                        #print(i[11])
                        #print(i[4])
                        #print(i[11].id)
                        art = ''
                        art = articulos.objects.filter(codigo=i[4], hospital_id=i[11].id).get('idsel')
                        print('idsel : ', str(art))
                        #cursor.execute( 'SELECT idsel FROM configuraciones_articulos WHERE codigo = %s',[ i[4] ] )
                        #i[5] = cursor.fetchone()[0] #AQUI esta la pk del articulo.
                        

                    except:
                        print('Fallo al insertar nuevo articulo')
                        #artnew = articulos(codigo=i[4] ,nombre=i[5] ,hospital=i[11])
                        #artnew.save()
                        consulta = "INSERT INTO configuraciones_articulos(codigo,nombre,hospital_id,foto)VALUES\
                        ('"+str(i[4])+"','"+str(art)+"','"+str(i[11].id)+"','"+str('articulos/fotos-'+codHosp+'/'+str(i[4])+'.png')+"')"
                        print(consulta)
                        cursor.execute( consulta )
                        print('Articulo_Nuevo: ' + str( art ))
                        cursor.execute( 'SELECT idsel FROM configuraciones_articulos WHERE codigo = %s',[ i[4] ] )
                        art = cursor.fetchone()[0]
                        
                    cursor.execute('SELECT gfh_id FROM configuraciones_dispositivos WHERE nombre = %s',[i[10] ])
                    #cursor.execute('SELECT id FROM configuraciones_gfhs WHERE gfh = %s',[i[9] ])
                    i[9] = str(cursor.fetchone()[0])
                    #print('pk_Gfh: ' + str(i[9]))
                    cursor.execute('SELECT id FROM configuraciones_dispositivos WHERE nombre = %s',[ str(i[10]) ] )
                    i[10] = str(cursor.fetchone()[0])
                    #print('pk_Disp: ' + str(i[10]))
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
                        "VALUES('"+str(i[0])+"','"+str(i[1])+"','"+str(i[2])+"','"+str(i[3])+"','"+str(i[4])+"','"+str(art)+"',\
                        '"+str(i[6])+"','"+str(i[7])+"','"+str(i[8])+"','"+str(i[9])+"','"+str(i[10])+"','"+str(i[11].id)+"')"
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

def download_fileMal(request):
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
                

            dispositivo = getIdDB(dispositivos.objects.filter(id=i.disp.id), 'nombre')
            gfhNombre = getIdDB(gfhs.objects.filter(id=i.gfh.id), 'gfh')
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
    nombre = ''
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

def adDispGfh( request ):
    gfh = None
    disp = None     # tabla disp = gfh_id , nombre
    hosp_id = None  # tabla gfh  = gfh, nombre , hp_id_id
    hosp_id = hospitales.objects.all().count()
    print('Numero Hospitales: ', str(hosp_id))
    if hosp_id == 0:
        msg = 'Antes de añadir dispositivos y gfhs es necesario crear un hospital.'
        return render(request, 'addDispGfh.html', {'mensaje': msg})

    if request.method == 'POST':
        if request.POST['addgfhC']:
            gfh = request.POST['addgfhC']
            if request.POST['hosp']:
                hosp_id = request.POST['hosp']
                if request.POST['addisp']:
                    disp = request.POST['addisp']
                    try:
                        dataGfh = gfhs(gfh=gfh, nombre=disp, hp_id_id=hospitales.objects.get(codigo=hosp_id).pk)
                        dataGfh.save()
                        dataDisp = dispositivos(gfh_id=dataGfh.id, nombre=disp)
                        dataDisp.save()
                    except Exception as e:
                        print('Error al crear gfh/disp.')
                        print(str(e))
    return render(request, 'addDispGfh.html')

def addHospital( request ):
    codigo = None
    hospital = None
    mensaje = None
    if request.method == 'POST':
        if request.POST['codhosp']:
            codigo = request.POST['codhosp']
            if request.POST['codisp']:
                hospital = request.POST['codisp']
                try:
                    ruta = 'articulos/fotos-'+codigo
                    hosp = hospitales(codigo=codigo, nombre=hospital, rutaFotos=ruta)
                    hosp.save()
                    fila = MEDIA_ROOT +'/' + 'articulos/fotos-'+ ruta
                    mkdir(fila)
                    mensaje = hosp.nombre+' creado correctamente'
                except Exception as e:
                    print('Error al crear hospital.')
                    print(str(e))


    return render(request, 'HospitalAdd.html', {'mensaje': mensaje})


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
    if request.method == 'POST':
        if request.POST['art']:
            nombre = request.POST['art']
            hospital = request.POST['hospi']
            print('Hospital: ', hospital )

    hosp_id = getIdDB( hospitales.objects.filter(codigo=hospital),'id' )
    print( 'Hosp_id: ', hosp_id )
    #cursor = connection.cursor()
    #articulos = cursor.execute('SELECT codigo, nombre, foto from configuraciones_articulos  WHERE nombre LIKE  %s  AND hospital_id = %s ',[ '%'+nombre+'%', hosp_id ])
    if nombre == "":
        nombre = "POQWERYEUUEYEUWYUYWUWYWY"

    try:
        #art = articulos.fetchall()
        art = articulos.objects.filter(nombre__contains=nombre, hospital_id=hosp_id)
        print(str(art))

    except Exception as e:
        print( 'Error: ', str(e) )


    return render( request , 'selarticulo.html',{ 'articulos': art } )

def GetAleatorio():
    import random
    rnd= ''
    l1 = 'A','B','C','D','E','F','G','H','I','X','Y','Z'
    for i in range(7):
        rnd += random.choice(l1)
    return rnd

def concatQS( qs):
    txt = ''
    tp = []
    tp2 = []
    for i in qs:
        for j in i:
            txt += '-' + str(j)
        tp.append([txt[1:]])
        txt = ''
    return tp
    #print('Item: ',str(tp))