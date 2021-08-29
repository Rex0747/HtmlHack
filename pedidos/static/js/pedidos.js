

$(document).ready(function(){

    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Pedido simple');

    Sgfh = $('#gfh');
    Sdisp = $('#disp');
    pboton2 = $('#pboton2');
    pboton = $('#pboton'); 
    user = $('#userlog');
    passwd =$('#passwd')
    pval = $('.pval').unbind().on('focusout', comprobar);
    //pboton2.click( envPacto );
    Sdisp.change( mostrarCampos );
    //pval = $('.pval').focusout( comprobar ); //focusout
    //$('.fecha').unbind().on('focus',function() {
    Sgfh.hide();
    Sdisp.hide();
    pboton2.hide();
    user.hide();
    passwd.hide();
    pboton.hide();
    //alert(user.val());
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
            Sdisp.html("<option value=''>SELECCIONE DISPOSITIVO</option>");
            for(let i=0; i<dataDev.length;i++){
                Sdisp.append(`<option value="${dataDev[i].ugs}">${dataDev[i].ugs}</option>`);
            }

            Sdisp.show();
        });
        
        //$('#cont1').hide();
    });

    function mostrarCampos(e){
        pboton2.show();
        user.show();
        passwd.show();
    }

    // function envPacto(e){
    //     Sgfh.hide();
    //     console.log('OCULTADO');
    // }

    function comprobar(e){
        //console.log(e.target.value);
        //console.log(e.target.id);
        $('#pboton').show();
        if (parseFloat( e.target.value ) > parseFloat( e.target.id )){
            //swal(`El valor introducido ${e.target.value} es mayor de el pactado ${e.target.id} continuar....?`)
            swal({  // manual y ejemplos ....https://blog.endeos.com/demo/sweetalert/index.html
                title: "Se supero la cantidad pedida a la pactada.",
                text: "Se pediran " + e.target.value + " y el pacto es de " + e.target.id ,
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "OK",
                cancelButtonText: "CANCELAR",
                closeOnConfirm: false,
                closeOnCancel: false },
                
                function(isConfirm){
                    if (isConfirm) {
                        swal("Confirmado",
                        "Se sobrepasan las unidades pedidas al pacto.",
                        "success");
                    } else {
                        swal("Cancelado",
                        "Se restaura pedido a cero.",
                        "error");
                        e.target.value = 0;
                        }
                    });
            
        }
    }
});

