
$(document).ready(function(){

    $('#Htitulo').text('SUBIR CAMBIOS EXCEL');
    $('#boton').click(enableBoton);
    $('#boton').attr("disabled", true);
    
    
    


    });


    function enableBoton(){
        $('#boton').attr("disabled", false);
        alert("Has pinchao");
        }