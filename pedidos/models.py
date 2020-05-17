from django.db import models
from configuraciones.models import articulos, dispositivos, gfhs, hospitales, configurations

# Create your models here.

class pedidos(models.Model):
    hospital=models.ForeignKey( hospitales ,on_delete=models.CASCADE )
    gfh=models.ForeignKey( gfhs ,on_delete=models.CASCADE )
    disp=models.ForeignKey( dispositivos ,on_delete=models.CASCADE )
    codigo=models.ForeignKey( articulos ,on_delete=models.CASCADE )
    cantidad=models.FloatField()

    

class usuarios(models.Model):
    nombre=models.CharField(max_length=30)
    ident= models.CharField(max_length=9, unique=True)
    passwd=models.CharField(max_length=100)











    
