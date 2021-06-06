

$(document).ready(function(){

    $(".loader").fadeOut("slow");
    $('#Htitulo').text('CONTROL DE GFHs');

    tabla = $('#tabla');
    //valor = $('select option:selected').attr('value');
    valor = $('#hosphidden').val();
    datos = { hospital: valor}

    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getHospital';
    
    $.getJSON(ruta, datos, function(dataDev){
        tabla.html("");
        tabla.append("<tr><th>GFH</th><th>LECTOR</th><th>DESCRIPCION</th></tr>");
        for(let i=0;i<dataDev.length;i++){
            tabla.append(`<tr><td><p>${dataDev[i].gfh}</p></td><td><p>${dataDev[i].nombre}</p></td><td><p>${dataDev[i].descripcion}</p></td></tr>`);
            
        }

    }  ).error(function(){
            alert('Fatal server error, intentalo luego de nuevo.')
    })
    
});

    




