from django.contrib import admin
from pedidos.models import pedidos, usuarios, pedidos_ident
# Register your models here.

admin.site.register(pedidos)
admin.site.register(usuarios)
admin.site.register(pedidos_ident)