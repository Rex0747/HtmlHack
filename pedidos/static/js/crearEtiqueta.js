$(document).ready(function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Añadir etiqueta');

    ptqr = $('#tqr').attr('id');
    valor = $('#'+ptqr).text();
    //console.log(valor);

    boton = $('#imprimir');
    boton.click(imprimir);

    ubicacion = '';
    codigo = '';
    nombre = '';
    pacto = 0;
    dc = '';
    gfh = '';
    disp = '';
    hospital = '';

});


function imprimir(){
    mtx = valor.split('|');
    ubicacion = mtx[0];
    codigo = mtx[1];
    nombre = mtx[2];
    pacto = mtx[3];
    dc = mtx[5];
    gfh = mtx[6];
    disp = mtx[7];
    hospital = mtx[8];
    
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getLineas';
    datos = { ubicacion: ubicacion, codigo: codigo, nombre: nombre, pacto: pacto, dc: dc, gfh: gfh, disp: disp, hospital: hospital};
    $.getJSON(ruta, datos, function(dataDev){

    for(let i=0;i<dataDev.length;i++){
        // $('#mensaje').append(`<p>${dataDev[i].mensaje}</p>`);
        window.confirm( dataDev[i].mensaje , "MENSAJE",
            "toolbar=no, location=no, directories=no, status=no, menubar=no, \
            scrollbars=no, resizable=no, copyhistory=no, width=400, height=200");
            }

    })


}