

$(document).ready(function(){

    $(".loader").fadeOut("slow");
    $('#Htitulo').text('CONTROL DE GFHs');
    $('#contGfhCod').hide();  
    $('#contDisp').hide();
    $('#contBt').hide();
    $('#subtitulo').hide();
    $('#contDescripcion').hide();
    

    $("#addhospC").change(function(){
        tabla = $('#tabla');
        valor = $('select option:selected').attr('value');
        datos = { hospital: valor}

        prot = document.location.protocol;
        loc = document.location.host;
        ruta = prot +'//'+ loc + '/getHospital';
        
        $.getJSON(ruta, datos, function(dataDev){

            tabla.append("<tr><th>GFH</th><th>LECTOR</th><th>DESCRIPCION</th></tr>");
            for(let i=0;i<dataDev.length;i++){
                tabla.append(`<tr><td><p>${dataDev[i].gfh}</p></td><td><p>${dataDev[i].nombre}</p></td><td><p>${dataDev[i].descripcion}</p></td></tr>`);
                
            }
            //alert(tabla.html())
            $('#contGfhCod').show();
            $('#contDisp').show();
            $('#contBt').show();
            $('#subtitulo').show();
            $('#contDescripcion').show();

        }  ).error(function(){
                alert('Fatal server error, intentalo luego de nuevo.')
        })
        
    });

    



})

function contHospCod(e){
    console.log('Entro.');
    alert('Entro');
    

    
}