

$(document).ready(function(){
    $('#Dgfh').hide();
    $('#Dugs').hide();
    $('#Dbajarfila').hide();
    $('#Dboton').hide();
    $('#Dcode').hide();


    $('#Shospital').change( Chospital );
    $('#Sgfh').change( Cugs); 
});


function Chospital(e)
{
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getHospital';
    datos = { hospital: e.target.value };

    $('#Sugs').html("<option value=''>SELECCIONE UGS</option>");
    Sgfh = $('#Sgfh');
    $.getJSON( ruta, datos, function(dataDev){
        Sgfh.html("");
        for(let i=0; i<dataDev.length;i++){
            //alert('DISP: '+dataDev[i].nombre +  '  GFH: '+ dataDev[i].gfh  );
            // Sugs.append(`<option value="${dataDev[i].nombre}">${dataDev[i].nombre}</option>`);
            Sgfh.append(`<option value="${dataDev[i].gfh}">${dataDev[i].gfh}</option>`);
        }
    $('#Dgfh').show();
    $('#Dcode').show();
    $('#Dboton').show();
    
    })
}

function Cugs(e)
{
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getUgs';
    Shospital = $('#Shospital option:selected').text();
    datos = { ugs: e.target.value, hospital: Shospital };
    //alert( e.target.value);

    Sugs = $('#Sugs');
    $.getJSON( ruta, datos, function(dataDev){
        Sugs.html("");
        for(let i=0;i<dataDev.length;i++){
            Sugs.append(`<option value="${dataDev[i].nombre}">${dataDev[i].nombre}</option>`);
        }
    $('#Dugs').show();
    $('#Dbajarfila').show();

    })

}





