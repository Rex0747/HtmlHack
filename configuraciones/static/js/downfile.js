
$(document).ready(function(){
    
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('CONTROL DE PACTOS');
    //$('#Dgfh').hide();
    $('#Dugs').hide();
    $('#Dbajarfila').hide();
    $('#Dboton').hide();
    $('#Dcode').hide();
    //$('#Shospital').change( Chospital );
    $('#Sgfh').change( Cugs );

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
            //alert('DISP: '+dataDev[i].nombre +  '  GFH: '+ dataDev[i].gfh  );
            // Sugs.append(`<option value="${dataDev[i].nombre}">${dataDev[i].nombre}</option>`);
            Sgfh.append(`<option value="${dataDev[i].gfh}">${dataDev[i].descripcion}</option>`);
        }
    //$('#Dgfh').show();
    $('#Dcode').show();
    $('#Dboton').show();
    
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
    $('#Dugs').show();
    $('#Dbajarfila').show();

    })

}





