

$(document).ready(function(){

    $('#contGfhCod').hide();  
    $('#contDisp').hide();
    $('#contBt').hide();
    $('#subtitulo').hide();

    $("#addhospC").change(function(){
    
        valor = $('select option:selected').attr('value');
        $('#prb').html("");
        datos = { hospital: valor}

        prot = document.location.protocol;
        loc = document.location.host;
        ruta = prot +'//'+ loc + '/getHospital';

        $.get(ruta, datos, function(dataDev){
            lista = dataDev.split('*');
            for(let i = 0 ; i < lista.length ; i++){
                $('#prb').append(`<p>${lista[i]}</p>`)
            }
            $('#contGfhCod').show();
            $('#contDisp').show();
            $('#contBt').show();
            $('#subtitulo').show();

        }  ).error(function(){
                alert('Fatal server error, intentalo luego de nuevo.')
        })
        
    });

    



})

function contHospCod(e){
    console.log('Entro.');
    alert('Entro');
    

    
}