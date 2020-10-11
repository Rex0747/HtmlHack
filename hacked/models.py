from django.db import models

# Create your models here.
class enlaces(models.Model):
    idsel = models.CharField(max_length=10, primary_key=True)
    link= models.CharField(max_length=100)

class datos(models.Model):
    idsel = models.CharField(max_length=10, primary_key=True)
    nombre_pagina=models.CharField(max_length=50)
    titulo=models.CharField(max_length=50)
    titulo_cont=models.CharField(max_length=50)
    dato = models.TextField()
    page = models.CharField(max_length=70)






    



