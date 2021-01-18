
var lat = 0.0;
var log = 0.0;
var foto = '';
var titulo = '';
var coment = '';
var link = '';

window.onload = function(){
    $(".loader").fadeOut("slow");
    $('#Htitulo').text('GESTION DE HOSPITALES');
    var mapa = document.getElementById('mapa');
    var lhosp = document.getElementById('dthosp');
    
    mapa.style.display = 'none';
    lhosp.addEventListener('change',(e)=>{

        prot = document.location.protocol;
        loc = document.location.host;
        ruta = prot +'//'+ loc;
        //alert(ruta);
        v = e.target.value;
        datosHosp = v.split('*');
        //hospital.setAttribute('src', ruta + '/media/'+ datosHosp[4]);
        //hospital.style.display = 'inline';
        titulo = datosHosp[1];
        lat = parseFloat(datosHosp[2]);
        log = parseFloat(datosHosp[3]);
        foto = ruta + '/media/'+ datosHosp[4];
        coment = datosHosp[5];
        link = datosHosp[6];
        
        initMap();
        mapa.style.display = 'block';
    });

};
    

window.initMap = function( ){
    //40.4414767, -3.7228253
    

    var v_posi = new google.maps.LatLng(lat , log);  //40.4414767,-3.7228253
    let v_mapa = new google.maps.Map(mapa,  {center: v_posi, zoom: 16, zoomControl: false ,
        disableDoubleClickZoom: true, scrollwheel: false,
        draggable: false, streetViewControl: true,
        streetViewControlOptions: {
        position: google.maps.ControlPosition.BOTTOM_TOP
        }});

    v_marca = new google.maps.LatLng( lat, log);
    const punto = new google.maps.Marker({position: v_marca, map: v_mapa});

		var v_contenidoInfo = '<h4>'+titulo+'</h4>'
        + '<img src='+foto+' />'
        + '<p>'+titulo+'<br ><br >'+coment+'</p>'
        + '<a  href='+link+'</a>';
        
        var v_info = new google.maps.InfoWindow({content: v_contenidoInfo});

        google.maps.event.addListener( punto, 'click', function() {
        
            v_info.open(v_mapa, punto);
            });

    };

