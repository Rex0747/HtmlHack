from pedidos.models import pedidos, pedidos_ident, pedidos_temp, usuarios, pedidos_dc, pedidos_ident_dc, addRefPedido
from rest_framework import fields, serializers

class ret_pedidos(serializers.ModelSerializer): #.HyperlinkedModelSerializer
    class Meta:
        
        model = pedidos
        fields = ['cantidad','codigo_id','disp_id','gfh_id','npedido','hospital_id']
        