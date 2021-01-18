$(document).ready(function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Enviar Pedidos');

    h=$('#h');
    u=$('#u');
    tabla = $('#tabla');
    tabla.hide();
    nelem = 0;

    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getPedTemp';

    datos = {  hospital: h.attr('value'), user: u.attr('value') };
    console.log(datos);
    
    $.getJSON( ruta, datos, function(dataDev){
        tabla.html("");
        tabla.append("<tr><th>CODIGO</th><th>NOMBRE</th><th>CANTIDAD</th><th>GFH</th><th>DISPOSITIVO</th><th>HOSPITAL</th></tr>");
        nelem = dataDev.length;
        for(let i=0;i<dataDev.length;i++){
            console.log( dataDev[i] );
            tabla.append(`<tr><td><p>${dataDev[i].codigo}</p></td><td><p>${dataDev[i].nombre}</p></td><td><p>${dataDev[i].cantidad}</p></td><td><p>${dataDev[i].gfh}</p></td><td><p>${dataDev[i].disp}</p></td><td><p>${dataDev[i].hospital}</p></td></tr>`);
        }

        if(nelem > 0){
            tabla.show();
            
        }

    });


});