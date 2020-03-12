from django.db import models

# Create your models here.

class articulos(models.Model):
    idsel = models.AutoField( primary_key=True )
    codigo=models.CharField(max_length=6 ) #, unique=True
    nombre=models.CharField(max_length=90)
    cbarras=models.CharField(max_length=50, null=True)
    cbarras2=models.CharField(max_length=50 , null=True)
    hospital=models.ForeignKey( 'hospitales' ,on_delete=models.CASCADE )
    foto=models.CharField( max_length=60 , null=True )#Contiene ruta a fichero de foto.

    def __str__(self):
        return '%s %s' %( self.codigo, self.nombre )

    class Meta:
        #pass
        #constraints = [
        #    models.UniqueConstraint( fields=['codigo', 'hospital'] )
        #]
        unique_together = ('codigo', 'hospital')


class gfhs(models.Model):
    id=models.AutoField( primary_key=True )
    gfh=models.CharField(max_length=4 ) #unique=True
    nombre=models.CharField(max_length=25)
    class Meta:
        unique_together = ('gfh', 'nombre')


class dispositivos(models.Model):
    id=models.AutoField( primary_key=True )
    nombre=models.CharField(max_length=5, unique=True)
    gfh=models.ForeignKey('gfhs', on_delete=models.CASCADE)  #, null=True, blank=True)
    class Meta:
        unique_together = ( 'nombre', 'gfh' )


class hospitales(models.Model):
    id=models.AutoField( primary_key=True )
    codigo=models.CharField(max_length=12 )  #unique=True
    nombre=models.CharField(max_length=30)


class configurations(models.Model):
    id=models.AutoField( primary_key=True )
    modulo=models.CharField(max_length=2 )
    estanteria=models.CharField(max_length=2 )
    ubicacion=models.CharField(max_length=5 )
    division=models.CharField(max_length=1 )
    codigo=models.CharField(max_length=6 )
    nombre=models.ForeignKey('articulos', on_delete=models.CASCADE ) #CharField(max_length=255 )
    pacto=models.FloatField( )
    minimo=models.FloatField( )
    dc=models.CharField(max_length=2 )
    gfh=models.CharField(max_length=8 ) 
    disp=models.CharField(max_length=6 )
    hosp= models.ForeignKey('hospitales',on_delete=models.CASCADE)


    def __str__(self):
        return '%s %s %s %s %s %s %s %s %s %s %s' %( 
            self.modulo,self.estanteria,self.ubicacion,
            self.division,self.codigo,self.nombre,self.pacto,
            self.minimo,self.dc,self.gfh,self.disp )

    class Meta: 
        unique_together = ( 'modulo','estanteria','ubicacion','division','disp' )




    