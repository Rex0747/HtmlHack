from django.db import models
from configuraciones.models import articulos, dispositivos, gfhs, hospitales, configurations

class stocks(models.Model):
    id=models.AutoField( primary_key=True )
    #modulo=models.CharField(max_length=2 )
    #estanteria=models.CharField(max_length=2 )
    #ubicacion=models.CharField(max_length=5 )
    #division=models.CharField(max_length=1 )
    codigo=models.CharField(max_length=6 )
    stock=models.FloatField( )
    dc=models.CharField(max_length=2 )
    gfh=models.ForeignKey(gfhs ,on_delete=models.CASCADE) 
    disp=models.ForeignKey(dispositivos ,on_delete=models.CASCADE)
    hosp= models.ForeignKey(hospitales ,on_delete=models.CASCADE)
    
    def __str__(self):
        return '%s %s %s %s %s %s' %( self.codigo, self.stock, self.dc, \
        self.gfh, self.disp, self.hosp )


class prueba(models.Model):
    prb=models.CharField(max_length=16)

    def __str__(self):
        return '%s' %(self.prb)




