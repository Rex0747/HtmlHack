$(document).ready(function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Stock referencia');

    fboton =$('#fenviar');
    //fboton.hide();
    calIni = $('#dat_ini');
    calFin = $('#dat_fin');
    codigo = $('#codigo');

    
    fboton.click( Eboton );
    //calIni.change( Cdate);
    //calFin.change( Cdate);
    //hosp.change(Chosp);
    Hospital = $('#hosphidden').val()
    //Chosp(Hospital);//hosphidden

});

function Eboton(){

    //hospi = Hospital //hosp.val();
    //alert(hospi);
    cal_ini = calIni.val();
    cal_fin = calFin.val();
    code = codigo.val();
    console.log(cal_ini);
    console.log(cal_fin);
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/stockref';
    //link = "<a href="+ prot +'//'+ loc + '/gpedidosdc?albaran=';
    datos = { cal_ini: cal_ini, cal_fin: cal_fin, codigo: code  };

    if(cal_ini && cal_fin && code){
        tabla=$('#tabla');
        suma = 0;
        $.getJSON( ruta, datos, function(dataDev){
            if (dataDev.length > 0){
                tabla.html("<tr><th>Pedido</th><th>Fecha</th><th>Codigo</th><th>Nombre</th><th>Cantidad</th><th>Disp</th><th>Gfh</th><th>Hospital</th></tr>");
                for(let i=0; i<dataDev.length;i++){
                    if(parseFloat(dataDev[i].cantidad) > 0){
                        tabla.append(`<tr><td>${dataDev[i].npedido}</td><td>${dataDev[i].fecha}</td><td>${dataDev[i].codigo}</td><td>${dataDev[i].nombre}</td><td>${dataDev[i].cantidad}</td><td>${dataDev[i].disp}</td><td>${dataDev[i].gfh}</td><td>${dataDev[i].hospital}</td></tr>`);
                        suma += parseFloat(dataDev[i].cantidad) 
                    }
                    else{
                        swal("ERROR", "No hay ninguna fila en ese rango de fechas", "error")
                    }
                    
                }
                swal({
                    title: "Consulta consumo de articulo",
                    text: "El numero de unidades consumidas es de " + parseFloat( suma),
                    timer: 5000,
                    showConfirmButton: false
                    });
            }
            else{
                //tabla.html("<p>No hay ningun pedido en ese rango de fechas.</p>");
                //alert("No hay ningun pedido en ese rango de fechas.")
                swal("ERROR", "No hay ninguna fila en ese rango de fechas", "error")
                }
            

            }
        )}
        

}