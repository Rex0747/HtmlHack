
$(document).ready(function(){

    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Pedido simple');

    Sgfh = $('#gfh');
    Sdisp = $('#disp');
    pboton2 = $('#pboton2');
    user = $('#user');
    passwd =$('#passwd')
    pval = $('.pval').focusout( comprobar ); //focusout
    Sgfh.hide();
    Sdisp.hide();
    pboton2.hide();
    user.hide();
    passwd.hide();

    //Shospital = $('#hospital');
    hospital = $('#hosphidden').val();
    CHospital(hospital);

    //Shospital.change(function(e){
    function CHospital( hospital ){
        prot = document.location.protocol;
        loc = document.location.host;
        ruta = prot +'//'+ loc + '/getHospital';
        datos = { hospital: hospital };
        
        $.getJSON( ruta, datos, function(dataDev){
            Sgfh.html("<option value=''>SELECCIONE GFH</option>");
            for(let i=0; i<dataDev.length;i++){
                Sgfh.append(`<option value="${dataDev[i].gfh}">${dataDev[i].descripcion}</option>`);
                console.log('Descripcion: '+dataDev[i].descripcion)
            }
            
            Sgfh.show();
        });
    };

    Sgfh.change(function(e){

        prot = document.location.protocol;
        loc = document.location.host;
        ruta = prot +'//'+ loc + '/getUgs';
        Shospital = $('#hospital option:selected').val();//.text();
        datos = { ugs: e.target.value, hospital: hospital };

        $.getJSON( ruta, datos, function(dataDev){
            Sdisp.html("<option value=''>SELECCIONE DSP</option>");
            for(let i=0; i<dataDev.length;i++){
                Sdisp.append(`<option value="${dataDev[i].ugs}">${dataDev[i].ugs}</option>`);
            }

            Sdisp.show();
            pboton2.show();
            user.show();
            passwd.show();
        });
        
        //$('#cont1').hide();
    });

    function comprobar(e){
        console.log(e.target.value);
        console.log(e.target.id);

    }
});

