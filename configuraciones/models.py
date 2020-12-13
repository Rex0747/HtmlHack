from django.db import models

# Create your models here.

class articulos(models.Model):
    idsel = models.AutoField( primary_key=True )
    codigo=models.CharField(max_length=6 ) #, unique=True
    nombre=models.CharField(max_length=90)
    cbarras=models.CharField(max_length=50, null=True)
    cbarras2=models.CharField(max_length=50 , null=True)
    hospital=models.ForeignKey( 'hospitales' ,on_delete=models.CASCADE )
    foto=models.ImageField( upload_to = 'articulos/' )

    def __str__(self):
        return '%s %s %s' %( self.codigo, self.nombre, self.foto )
        #return '%s' %( self.nombre )

    class Meta:
        #pass
        #constraints = [
        #    models.UniqueConstraint( fields=['codigo', 'hospital'] )
        #]
        unique_together = ('codigo', 'hospital')
        
    class Admin:
        list_display = ('codigo', 'nombre', 'hospital_id')
        list_filter = ('hospital_id',)
        ordering = ('-codigo',)
        search_fields = ('codigo',)

class gfhs(models.Model):
    id=models.AutoField( primary_key=True )
    gfh=models.CharField(max_length=4 ) #unique=True
    nombre=models.CharField(max_length=25, unique=True)
    hp_id=models.ForeignKey( 'hospitales' , models.SET_NULL,blank=True, null=True )
    def __str__(self):
        return '%s %s' %(self.gfh, self.nombre)

    class Meta:
        unique_together = ('gfh', 'nombre')


class dispositivos(models.Model):
    id=models.AutoField( primary_key=True )
    nombre=models.CharField(max_length=6, unique=True)
    gfh=models.ForeignKey('gfhs', on_delete=models.CASCADE)  #, null=True, blank=True)
    def __str__(self):
        return '%s %s' %(self.nombre, self.gfh)
    class Meta:
        unique_together = ( 'nombre', 'gfh' )


class hospitales(models.Model):
    id=models.AutoField( primary_key=True )
    codigo=models.CharField(max_length=12, unique=True )  #unique=True
    nombre=models.CharField(max_length=30)
    rutaFotos=models.CharField(max_length=30, null=True, blank=True)
    longitud=models.CharField(max_length=15, null=True, blank=True)
    latitud=models.CharField(max_length=15, null=True, blank=True)
    comentario=models.TextField(max_length=1024,null=True, blank=True)
    link=models.CharField(max_length=255,null=True, blank=True)
    foto=models.ImageField( upload_to = 'articulos/', null=True, blank=True )
    def __str__(self):
        return '%s %s %s' %( self.codigo, self.nombre, self.rutaFotos )
        

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
    gfh=models.ForeignKey('gfhs', on_delete=models.CASCADE ) 
    disp=models.ForeignKey('dispositivos', on_delete=models.CASCADE )
    hosp= models.ForeignKey('hospitales',on_delete=models.CASCADE)
    #nconfig= models.CharField(max_length=8, unique=False)
    nconfig= models.IntegerField(unique=False)
    fechalta= models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s %s %s %s %s %s %s %s %s %s %s %s %s %s' %( 
            self.modulo,self.estanteria,self.ubicacion,
            self.division,self.codigo,self.nombre,self.pacto,
            self.minimo,self.dc,self.gfh,self.disp,self.hosp,self.nconfig,self.fechalta)

    class Meta: 
        unique_together = ( 'modulo','estanteria','ubicacion','division','disp','hosp','gfh','nconfig' ) 


class excel(models.Model):
    modulo=models.CharField(max_length=2 )
    estanteria=models.CharField(max_length=2 )
    ubicacion=models.CharField(max_length=5 )
    division=models.CharField(max_length=1 )
    codigo=models.CharField(max_length=6 )
    nombre=models.ForeignKey('articulos', on_delete=models.CASCADE )
    pacto=models.FloatField( )
    minimo=models.FloatField( )
    dc=models.CharField(max_length=2 )
    gfh=models.ForeignKey('gfhs', on_delete=models.CASCADE ) 
    disp=models.ForeignKey('dispositivos', on_delete=models.CASCADE )
    hosp= models.ForeignKey('hospitales',on_delete=models.CASCADE)

    def __str__(self):
        return '%s %s %s %s %s %s %s %s %s %s %s %s' %( 
            self.modulo,self.estanteria,self.ubicacion,
            self.division,self.codigo,self.nombre,self.pacto,
            self.minimo,self.dc,self.gfh,self.disp,self.hosp )

    class Meta: 
        unique_together = ( 'modulo','estanteria','ubicacion','division','disp','hosp' ) 

