// //________________PRUEBAS EXCEL__________________

// //___________END PRUEBAS EXCEL


var mtx = [];
var mtx_filtro = [];
var rm = 0;

$(document).ready(function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('FILTROS');
    tabla = $('#tabla');
    tabla.hide();
    $('#Dfiltro').hide();
    $('#Bexcel').click( bclick );
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


async function getData(){
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
    tabla.append("<tr><th>MOD</th><th>EST</th><th>UBI</th><th>DIV</th><th>CODIGO</th><th>NOMBRE</th><th>PACTO</th><th>DC</th></tr>");
    //if( rm == 0){
    await $.getJSON( ruta, datos, function(dataDev){
        mtx = [];
        for(let i=0; i<dataDev.length;i++){
            mtx.push(dataDev[i]);
            mtx_filtro.push(dataDev[i]);
            tabla.append(`<tr><td><p>${dataDev[i].modulo}</p></td><td><p>${dataDev[i].estanteria}</p></td><td><p>${dataDev[i].ubicacion}</p></td><td><p>${dataDev[i].division}</p></td><td><p>${dataDev[i].codigo}</p></td><td><p>${dataDev[i].nombre}</p></td><td><p>${dataDev[i].pacto}</p></td><td><p>${dataDev[i].dc}</p></td></td></tr>`);
            
        }
      //  rm ++;
        
        });
        tabla.show();
        $('#Dfiltro').show();
        //$('#Dgetdatos').hide();

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
    tabla.append("<tr><th>MOD</th><th>EST</th><th>UBI</th><th>DIV</th><th>CODIGO</th><th>NOMBRE</th><th>PACTO</th><th>MINIMO</th><th>DC</th></tr>");

    for(let i = 0; i < mtx_filtro.length; i++){
        tabla.append(`<tr><td><p>${mtx_filtro[i].modulo}</p></td><td><p>${mtx_filtro[i].estanteria}</p></td><td><p>${mtx_filtro[i].ubicacion}</p></td><td><p>${mtx_filtro[i].division}</p></td><td><p>${mtx_filtro[i].codigo}</p></td><td><p>${mtx_filtro[i].nombre}</p></td><td><p>${mtx_filtro[i].pacto}</p></td><td><p>${mtx_filtro[i].minimo}</p></td><td><p>${mtx_filtro[i].dc}</p></td></td></tr>`);

    }
    
    tabla.show();
    $('#Linfo').text( mtx_filtro.length + ' FILAS FILTRADAS.');
}

function s2ab(s) { 
    var buf = new ArrayBuffer(s.length); //convert s to arrayBuffer
    var view = new Uint8Array(buf);  //create uint8array as viewer
    for (var i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF; //convert to octet
    return buf;    
    }

function bclick(){
    if (mtx_filtro.length == 0)
        return
    var wb = XLSX.utils.book_new();
    wb.Props = {
    Title: "SheetJS Pruebas",
    Subject: "Test",
    Author: "Pedro Luis",
    CreatedDate: new Date(2021,06,14)
    };
    
    wb.SheetNames.push("Test Sheet");
    //var ws_data = [['hello' , 'world'],['Hola','Amigo'],[1,2,3,4,5,6,7,8]]; 
    var ws_data = ConvertirMtx( mtx_filtro );
    var ws = XLSX.utils.aoa_to_sheet( ws_data );
    wb.Sheets["Test Sheet"] = ws;
    var wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});

    {saveAs(new Blob([s2ab(wbout)],{type:"application/octet-stream"}), 'file.xlsx');
        }
    };

    function ConvertirMtx( mtz ){

        ret = [];
        mtx = [];

        mtx.push( 'Modulo' );
        mtx.push( 'Estanteria' );
        mtx.push( 'Ubicacion' );
        mtx.push( 'Division' );
        mtx.push( 'Codigo' );
        mtx.push( 'Nombre' );
        mtx.push( 'Pacto' );
        mtx.push( 'Minimo' );
        mtx.push( 'DC' );

        ret.push( mtx );
        mtx = [];

        for(let i = 0; i < mtz.length; i++){
                mtx.push( mtz[i].modulo );
                mtx.push( mtz[i].estanteria );
                mtx.push( mtz[i].ubicacion );
                mtx.push( mtz[i].division );
                mtx.push( mtz[i].codigo );
                mtx.push( mtz[i].nombre );
                mtx.push( mtz[i].pacto );
                mtx.push( mtz[i].minimo );
                mtx.push( mtz[i].dc );

                ret.push( mtx );
                mtx = [];
            
        }
        return ret;
    }