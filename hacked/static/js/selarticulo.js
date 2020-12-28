$(document).ready(function(){

    $('#Htitulo').text('BUSQUEDA REFERENCIAS');
    $('#Shospi').change( enableBoton );
    $('#boton').hide();
    $('#art').mouseout( enableBoton );
    
    
    });


    function enableBoton(e){
        
        Ctexto = $('#art').val();
        if(e.target.value != '' && Ctexto != ''){
            $('#boton').show();
            
            }
        }