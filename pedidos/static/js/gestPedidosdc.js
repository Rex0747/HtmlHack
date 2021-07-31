$(document).ready(function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Gestion pedidos DC');

    fboton =$('#fenviar');
    fboton.hide();
    calIni = $('#dat_ini');
    calFin = $('#dat_fin');
    

    //hosp = $('#Shospital'),
    fboton.click( Eboton );
    calIni.change( Cdate);
    calFin.change( Cdate);
    //hosp.change(Chosp);
    Hospital = $('#hosphidden').val();
    Chosp(Hospital);//hosphidden

});

function Chosp(){
    if(calIni.val() != "" && calFin.val() != "" ){ 
        
    }
}

function Cdate(){
    if(calIni.val() != "" && calFin.val() != "" ){ 
        fboton.show();
    }

}

function Eboton(){

    hospi = Hospital //hosp.val();
    //alert(hospi);
    cal_ini = calIni.val();
    cal_fin = calFin.val();
    console.log(cal_ini);
    console.log(cal_fin);
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getAlbaranesdc';
    link = "<a href="+ prot +'//'+ loc + '/gpedidosdc?albaran=';
    datos = { cal_ini: cal_ini, cal_fin: cal_fin, hospital: hospi };

    if(cal_ini && cal_fin){
        tabla=$('#tabla');
        $.getJSON( ruta, datos, function(dataDev){
            if (dataDev.length > 0){
                tabla.html("<tr><th>Albaran</th><th>Fecha</th><th>Hospital</th><th>Enlace</th></tr>");
                for(let i=0; i<dataDev.length;i++){
                    tabla.append(`<tr><td>${dataDev[i].albaran}</td><td>${dataDev[i].fecha}</td><td>${dataDev[i].hospital}</td><td class=link>${link}${dataDev[i].albaran}><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left-circle" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-4.5-.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5H11.5z"/></svg></a></td></tr>`);
                    //console.log(dataDev[i].fecha)
                }
            }
            else{
                //tabla.html("<p>No hay ningun pedido en ese rango de fechas.</p>");
                //alert("No hay ningun pedido en ese rango de fechas.")
                swal("ERROR", "No hay ninguna fila en ese rango de fechas", "error")
                }
            

            }
        )}   

}