

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

        $.getJSON(ruta, datos, function(dataDev){

            for(let i=0;i<dataDev.length;i++){
                $('#prb').append(`<p>${dataDev[i].gfh}&nbsp&nbsp&nbsp&nbsp&nbsp${dataDev[i].nombre}</p>`)
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