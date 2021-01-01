

$(document).ready(function(){

    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Modificar pactos');
    boton = $('#boton');
    tabla = $('#tabla');
    despHospital = $('#selHospC');
    despGfh = $('#selGfh');
    despDisp = $('#selDisp');

    despGfh.hide();
    despDisp.hide();
    boton.hide();
    
    despHospital.change(CHospital); 
    despGfh.change( Cgfh);
    despDisp.change( Cdisp);
});

function CHospital(e){

    alert(e.target.value);
    console.log(e.target.value);
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getHospital';
    datos = { hospital: e.target.value };
    despGfh.show();

    $.getJSON( ruta, datos, function(dataDev){
        //despGfh.html("");
        despGfh.html("<option value=''>SELECCIONE GFH</option>");
        for(let i=0; i<dataDev.length;i++){
            //alert('DISP: '+dataDev[i].nombre +  '  GFH: '+ dataDev[i].gfh  );
            // Sugs.append(`<option value="${dataDev[i].nombre}">${dataDev[i].nombre}</option>`);
            despGfh.append(`<option value="${dataDev[i].gfh}">${dataDev[i].gfh}</option>`);
        }


    despGfh.style.display = 'block';


    });
}

function Cgfh(e){


    boton.style.display = 'block';
    tabla.style.display = 'block';
};

function Cdisp(){
    alert('ENTRO');

}

function mostrarTabla(){
    $('#tabla').style.display = 'block';
    
}