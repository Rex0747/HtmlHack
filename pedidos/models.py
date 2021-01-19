from django.db import models
from configuraciones.models import articulos, dispositivos, gfhs, hospitales, excel, configurations

# Create your models here.
class datos_email(models.Model):
    ucorreo = models.EmailField(max_length=50, null=False)
    #item[0] = passwd, item[1] = emisor correo, item[2] = correo recepcion

    def __str__(self):
        return '%s' %(self.ucorreo)

class usuarios(models.Model):
    nombre=models.CharField(max_length=50)
    ident= models.CharField(max_length=9, unique=True)
    passwd=models.CharField(max_length=100, null=False)
    correo=models.EmailField(max_length=50, null=False)

    def __str__(self):
        return '%s %s %s' %(self.nombre, self.ident, self.correo)

class pedidos(models.Model):
    npedido=models.CharField(max_length=12)
    gfh=models.ForeignKey( gfhs ,on_delete=models.CASCADE )
    disp=models.ForeignKey( dispositivos ,on_delete=models.CASCADE )
    codigo=models.ForeignKey( articulos  ,on_delete=models.CASCADE )
    cantidad=models.FloatField()

    def __str__(self):
        return '%s %s %s %s %s' %( self.npedido, self.gfh, self.disp, self.codigo, self.cantidad )

class pedidos_dc(models.Model):
    npedido=models.CharField(max_length=12)
    codigo=models.ForeignKey( articulos  ,on_delete=models.CASCADE )
    cantidad=models.FloatField()
    disp=models.ForeignKey(dispositivos, on_delete=models.CASCADE )
    gfh=models.ForeignKey( gfhs ,on_delete=models.CASCADE )

    def __str__(self):
        return '%s %s %s %s %s' %( self.npedido, self.hospital, self.gfh, self.codigo, self.cantidad )

class pedidos_temp(models.Model):
    hospital=models.ForeignKey( hospitales ,on_delete=models.CASCADE )
    gfh=models.ForeignKey( gfhs ,on_delete=models.CASCADE )
    disp=models.ForeignKey( dispositivos ,on_delete=models.CASCADE )
    codigo=models.ForeignKey( articulos  ,on_delete=models.CASCADE )
    cantidad=models.FloatField()
    user_temp=models.ForeignKey( usuarios ,on_delete=models.CASCADE)

class pedidos_ident(models.Model):
    pedido=models.CharField(max_length=12)
    user=models.ForeignKey( usuarios ,on_delete=models.CASCADE)
    fecha=models.DateTimeField(auto_now=True)
    hospital=models.ForeignKey( hospitales ,on_delete=models.CASCADE )

    def __str__(self):
        return '%s %s %s %s' %( self.pedido, self.user, self.fecha, self.hospital)

class pedidos_ident_dc(models.Model):
    pedido=models.CharField(max_length=12)
    fecha=models.DateTimeField(auto_now=True)
    hospital=models.ForeignKey( hospitales ,on_delete=models.CASCADE )
    
    def __str__(self):
        return '%s %s' %( self.pedido, self.fecha)

class addRefPedido( models.Model):
    ubicacion = models.CharField(max_length=12)
    codigo = models.CharField(max_length=6)
    nombre = models.CharField(max_length=100)
    pacto = models.IntegerField()
    dc = models.CharField(max_length=1)
    gfh = models.CharField(max_length=4)
    disp = models.CharField(max_length=6)
    hospital = models.CharField(max_length=4)

    def __str__(self):
        return '%s %s %s %s %s %s %s %s' %( self.ubicacion,self.codigo,self.nombre,self.pacto,self.dc,self.gfh,self.disp,self.hospital  )







    
