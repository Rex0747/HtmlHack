from django.contrib import admin
from configuraciones.models import articulos , configurations , dispositivos, gfhs, hospitales

# Register your models here.

admin.site.register(articulos)
admin.site.register(configurations)
admin.site.register(dispositivos)
admin.site.register(gfhs)
admin.site.register(hospitales)