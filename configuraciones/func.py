
from configuraciones.models import articulos, configurations , hospitales, gfhs , dispositivos
from django.db.models import Max
import json 

class funcConf:


    @staticmethod
    def GetAleatorio():
        import random
        rnd= ''
        l1 = 'A','B','C','D','E','F','G','H','I','X','Y','Z'
        for i in range(7):
            rnd += random.choice(l1)
        return rnd

    @staticmethod
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

    @staticmethod
    def audio():
        # -*- coding: utf-8 -*-
        """
        Created on Tue Oct 27 22:24:01 2020

        @author: Pedro
        """

        from gtts import gTTS
        from pygame import mixer
        from playsound import playsound
        from os import  remove


        texto = "gfh y dispositivo creado correctamente."
        idioma = 'es'

        audio = gTTS(text = texto,  lang = idioma, slow = False )
        audio.save('C:/temp/prueba.mp3')


        sound = r"C:/temp/prueba.mp3"
        playsound(sound)
        remove("C:/temp/prueba.mp3")

    @staticmethod
    def SetMaxId():
        c1 = None
        idconfig = None
        try:
            c1 = configurations.objects.all()#.count()
            idconfig = c1.aggregate(Max('nconfig'))
            print( str('idconfig: ', str(idconfig)))
        except Exception as e:
            print('Error Consulta:', str(e))
            print( str( idconfig))
        #print( str( idconfig))
        if idconfig['nconfig__max'] == None:
            return 0
        else:
            return idconfig['nconfig__max'] + 1
            

    @staticmethod
    def SetMaxId_gfh(gfh, disp, hosp):
        c1 = None
        try:
            c1 = configurations.objects.filter(gfh=gfh,disp=disp,hosp=hosp)#.count()
            idconfig = c1.aggregate(Max('nconfig'))
            print( str('idconfig: ', str(idconfig)))
        except Exception as e:
            print('Error Consulta:', str(e))
            print( str( idconfig))
        #print( str( idconfig))
        idconfig  = idconfig['nconfig__max']
        return idconfig

#-----------------------------JSON----------------------------------------------------------------



class Json:
    jeiso = "["
    #bloque = """{"gfh": "","nombre": "" """  
    bloque = None
    def __init__(self, bloque ):
        self.bloque = bloque
        print('Bloque: ', self.bloque)
    def crearJson(self,data):
        j = 0
        for i in range(len(data)):
            if j < len(data) -1:
                self.jeiso += self.bloque + "},"
                j += 1
            else:
                self.jeiso += self.bloque + "}"
                        
        self.jeiso += "]"
        v = json.loads(self.jeiso)
        j = 0
        k = 0
        claves = []
        print('V0: ', v )
        for i in v:
            for s in i.keys():
                claves.append(str(s))
            break
        print('Claves: ', claves)
        for i in v:
            k = 0
            for x in i:
                cl = claves[k]
                i[cl] = data[j][k]
                k += 1
            j += 1
        #print('Res: ',str(v))
        return json.dumps(v)