from django.db import models
from configuraciones.models import articulos, dispositivos, gfhs, hospitales, configurations

# Create your models here.

class usuarios(models.Model):
    nombre=models.CharField(max_length=30)
    ident= models.CharField(max_length=9, unique=True)
    passwd=models.CharField(max_length=100, null=False)
    correo=models.EmailField(max_length=30, null=False)

    def __str__(self):
        return '%s %s %s' %(self.nombre, self.ident, self.correo)

class pedidos(models.Model):
    npedido=models.CharField(max_length=12)
    hospital=models.ForeignKey( hospitales ,on_delete=models.CASCADE )
    gfh=models.ForeignKey( gfhs ,on_delete=models.CASCADE )
    disp=models.ForeignKey( dispositivos ,on_delete=models.CASCADE )
    codigo=models.ForeignKey( articulos  ,on_delete=models.CASCADE )
    cantidad=models.FloatField()

    def __str__(self):
        return '%s %s %s %s %s %s' %( self.npedido, self.hospital, self.gfh, self.disp, self.codigo, self.cantidad )

class pedidos_ident(models.Model):
    pedido=models.CharField(max_length=12)
    user=models.ForeignKey( usuarios ,on_delete=models.CASCADE)
    fecha=models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s %s %s' %( self.pedido, self.user, self.fecha)












    
