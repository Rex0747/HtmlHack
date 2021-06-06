var mtx = [];
var mtx_filtro = [];
var rm = 0;

$(document).ready(function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('FILTROS');
    tabla = $('#tabla');
    tabla.hide();
    $('#Bgetdatos').click( getData );
    $('#bfiltro').click( FiltroCodigo );
    $('#Sgfh').change( Cugs );

    $('#Dgetdatos').hide();
    

    Hospital = $('#hosphidden').val()
    Chospital(Hospital);//hosphidden

});

function Chospital(e)
{
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getHospital';
    datos = { hospital: e }; //datos = { hospital: e.target.value };

    Sgfh = $('#Sgfh');
    $.getJSON( ruta, datos, function(dataDev){
        Sgfh.html("<option value=''>SELECCIONE GFH</option>");
        for(let i=0; i<dataDev.length;i++){
            Sgfh.append(`<option value="${dataDev[i].gfh}">${dataDev[i].descripcion}</option>`);
        }
        

    
    })
}

function Cugs(e)
{
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getUgs';
    Shospital = $('#Shospital option:selected').val();  //text();
    datos = {  hospital: Hospital, ugs: e.target.value };
    //alert( e.target.value);

    Sugs = $('#Sugs');
    $.getJSON( ruta, datos, function(dataDev){
        Sugs.html("<option value=''>SELECCIONE UGS</option>");
        for(let i=0;i<dataDev.length;i++){
            Sugs.append(`<option value="${dataDev[i].ugs}">${dataDev[i].ugs}</option>`);
        }
        $('#Dgetdatos').show();

    })

}


function getData(){
    var hosp = $('#hosphidden').val();
    //var gfh = $('#Tgfh').val();
    //var disp = $('#Tdisp').val();
    var gfh = $('#Sgfh').val();
    var disp = $('#Sugs').val();

    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getConfGfh';
    datos = { hospital: hosp , gfh: gfh, disp: disp };
    //console.log( datos );
    tabla.html("");
    tabla.append("<tr><th>M</th><th>E</th><th>U</th><th>D</th><th>CODIGO</th><th>NOMBRE</th><th>PACTO</th><th>MINIMO</th><th>DC</th></tr>");
    //if( rm == 0){
    $.getJSON( ruta, datos, function(dataDev){
        mtx = [];
        for(let i=0; i<dataDev.length;i++){
            mtx.push(dataDev[i]);
            tabla.append(`<tr><td><p>${dataDev[i].modulo}</p></td><td><p>${dataDev[i].estanteria}</p></td><td><p>${dataDev[i].ubicacion}</p></td><td><p>${dataDev[i].division}</p></td><td><p>${dataDev[i].codigo}</p></td><td><p>${dataDev[i].nombre}</p></td><td><p>${dataDev[i].pacto}</p></td><td><p>${dataDev[i].minimo}</p></td><td><p>${dataDev[i].dc}</p></td></td></tr>`);
            
        }
      //  rm ++;
        
        });
        tabla.show();
        $('#Dgetdatos').hide();

        $('#Linfo').text(mtx.length + ' FILAS EN DISPOSITIVO.')
    //}
}

function FiltroCodigo(){
    var code = $('#filtro').val().toUpperCase();
    mtx_filtro = mtx.filter( mtxs => mtxs.codigo == code );
    if( mtx_filtro.length == 0 ){
        mtx_filtro = mtx.filter( mtxs => mtxs.nombre.includes( code ));
    }
    tabla.html("");
    tabla.append("<tr><th>M</th><th>E</th><th>U</th><th>D</th><th>CODIGO</th><th>NOMBRE</th><th>PACTO</th><th>MINIMO</th><th>DC</th></tr>");

    for(let i = 0; i < mtx_filtro.length; i++){
        //var h3 = document.createElement("h3");
        //h3.innerText = mtx_filtro[i].codigo + ' ' + mtx_filtro[i].nombre + ' ' + mtx_filtro[i].pacto;
        //document.body.appendChild(h3);
        tabla.append(`<tr><td><p>${mtx_filtro[i].modulo}</p></td><td><p>${mtx_filtro[i].estanteria}</p></td><td><p>${mtx_filtro[i].ubicacion}</p></td><td><p>${mtx_filtro[i].division}</p></td><td><p>${mtx_filtro[i].codigo}</p></td><td><p>${mtx_filtro[i].nombre}</p></td><td><p>${mtx_filtro[i].pacto}</p></td><td><p>${mtx_filtro[i].minimo}</p></td><td><p>${mtx_filtro[i].dc}</p></td></td></tr>`);

    }
    
    tabla.show();
    $('#Linfo').text( mtx_filtro.length + ' FILAS FILTRADAS.');
}
