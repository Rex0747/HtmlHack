from django.contrib import admin
from pedidos.models import pedidos, usuarios, pedidos_ident, pedidos_dc,pedidos_ident_dc
# Register your models here.

admin.site.register(pedidos)
admin.site.register(usuarios)
admin.site.register(pedidos_ident)
admin.site.register(pedidos_dc)
admin.site.register(pedidos_ident_dc)