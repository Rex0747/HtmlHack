$(document).ready(function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('CRUD PEDIDOS');
    fboton =$('#fenviar');
    calIni = $('#dat_ini');
    //fboton.click( Eboton );

    Hospital = $('#hosphidden').val();
    calIni.change( Cdate);
    Hospital = $('#hosphidden').val();
});


function Cdate(){
    //alert('Cambio fecha');
    cal_ini = calIni.val();
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/addLineaPedidoDc';
    datos = { cal_ini: cal_ini, hospital: Hospital };
    if(cal_ini){
        tabla=$('#tabla');
        $.getJSON( ruta, datos, function(dataDev){
            if (dataDev.length > 0){
                alert('datos Recibidos');
            }
            else
            {
                alert('No hay datos con ese criterio.');
            }
        })
    }
}
    
    