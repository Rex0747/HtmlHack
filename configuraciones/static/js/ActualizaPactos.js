

$(document).ready(function(){

    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Modificar pactos');
    boton = $('#boton');
    tabla = $('#tabla');
    despHospital = $('#selHosp');
    despGfh = $('#selGfh');
    despDisp = $('#selDisp');

    despGfh.hide();
    despDisp.hide();
    tabla.hide();
    
    despHospital.change(CHospital);
    despGfh.change( Cgfh);
    despDisp.change( Cdisp);
});

function CHospital(e){

    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getHospital';
    datos = { hospital: e.target.value };
    despGfh.show();

    $.getJSON( ruta, datos, function(dataDev){
    despGfh.html("<option value=''>SELECCIONE GFH</option>");
    for(let i=0; i<dataDev.length;i++){
        despGfh.append(`<option value="${dataDev[i].gfh}">${dataDev[i].gfh}</option>`);
    }
    despGfh.show();
}); 
    

}

function Cgfh(e){
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getUgs';
    Shospital = $('#selHosp option:selected').text();
    datos = {  hospital: Shospital,  ugs: e.target.value };
    Sugs = $('#selDisp');
    $.getJSON( ruta, datos, function(dataDev){
        console.log(JSON.stringify(dataDev));
        Sugs.html("<option value=''>SELECCIONE DSP</option>");

        for(let i=0;i<dataDev.length;i++){
            Sugs.append(`<option value="${dataDev[i].ugs}">${dataDev[i].ugs}</option>`);
        }

        despDisp.show();
        //boton.show();
    });
    
};

function Cdisp(e){
    //alert('ENTRO');
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getConf';
    Shospital = $('#selHosp option:selected').text();
    Sgfh = $('#selGfh option:selected').text();
    datos = { ugs: e.target.value, hospital: Shospital, gfh: Sgfh  };
    //console.log(Shospital + ' ' + Sgfh + ' ' + e.target.value )
    $.getJSON( ruta, datos, function(dataDev){
        //Stabla = $('#tabla');
        tabla.html("");
        //Stabla.append('<table id="tabla" class="config">');
        tabla.append("<tr><th>REFERENCIA</th><th>DESCRIPCION</th><th>NUEVO</th><th>PACTO</th></tr>");
        
        for(let i=0;i<dataDev.length;i++){
            tabla.append(`<tr><td><p>${dataDev[i].codigo}</p></td><td><p>${dataDev[i].nombre}</p></td><td><input type='text' name='${dataDev[i].codigo}*${dataDev[i].modulo}*${dataDev[i].estanteria}*${dataDev[i].ubicacion}*${dataDev[i].division}' value='' class='input-group-text' onkeypress="return event.charCode >= 48 && event.charCode <= 57"></td><td>${dataDev[i].pacto}</td></tr>`); 
            //console.log(`<tr><td><p>${dataDev[i].codigo}</p></td><td><p>${dataDev[i].nombre}</p></td><td><input type='text' name='${dataDev[i].codigo}*${dataDev[i].modulo}*${dataDev[i].estanteria}*${dataDev[i].ubicacion}*${dataDev[i].division}' value='' class='input-group-text'></td><td>PACTO:${dataDev[i].pacto}</td></tr>`);
        }
        
        tabla.show();
        //DcontPacto = $('#contPacto');
        //DcontPacto.append("<input type='submit' id='boton' value='Modificar' class='btn-outline-primary'>");
    
    
    });
}
