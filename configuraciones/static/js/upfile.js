
$(document).ready(function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('SUBIR CAMBIOS EXCEL');
    $('#upload').mouseout(enableBoton);
    $('#boton').attr("disabled", true);
    Cfile = $('#upload');
    
    
    });


function enableBoton(e){
    if(e.target.value != '')
        $('#boton').attr("disabled", false);
    
    }
