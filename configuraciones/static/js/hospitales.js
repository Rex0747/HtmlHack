var codigo = '';
var lat = 0.0;
var log = 0.0;
var foto = '';
var titulo = '';
var coment = '';
var link = ''; 

//window.onload = function(){
$(document).ready(function(){
    //initMap();
    /* $(".loader").fadeOut("slow");
    $('#Htitulo').text('GESTION DE HOSPITALES');
    var mapa = document.getElementById('mapa');
    //var lhosp = document.getElementById('hosphidden')  //('dthosp');
    var hospital = $('#hosphidden').val()
    mapa.style.display = 'none';
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getDatosHospital';
    datos = { hospital: hospital }
    $.getJSON( ruta, datos, function(dataDev){
        for(let i=0; i < 1 ;i++){
            codigo = dataDev[i].codigo
            titulo = dataDev[i].nombre;
            lat = dataDev[i].latitud;
            log = dataDev[i].longitud;
            foto = '/media/'+ dataDev[i].foto;
            coment = dataDev[i].comentario;
            link = dataDev[i].link;
            }

    initMap();
    mapa.style.display = 'block';
    });
 */
    
}) ; 



//window.initMap = function( ){
async function initMap()
{

    $(".loader").fadeOut("slow");
    $('#Htitulo').text('GESTION DE HOSPITALES');
    var mapa = document.getElementById('mapa');
    //var lhosp = document.getElementById('hosphidden')  //('dthosp');
    var hospital = $('#hosphidden').val()
    mapa.style.display = 'none';
    prot = document.location.protocol;
    loc = document.location.host;
    ruta = prot +'//'+ loc + '/getDatosHospital';
    datos = { hospital: hospital }
    await $.getJSON( ruta, datos, function(dataDev){
        for(let i=0; i < 1 ;i++){
            codigo = dataDev[i].codigo
            titulo = dataDev[i].nombre;
            lat = dataDev[i].latitud;
            log = dataDev[i].longitud;
            foto = '/media/'+ dataDev[i].foto;
            coment = dataDev[i].comentario;
            link = dataDev[i].link;
        }

    //initMap();
    mapa.style.display = 'block';
    });

    //-----------------------------------------------------------------------------
    //40.4414767, -3.7228253
    let v_posi = new google.maps.LatLng(log , lat);  //40.4414767,-3.7228253
    let v_mapa = new google.maps.Map(mapa,  {center: v_posi, zoom: 16, zoomControl: true ,
        disableDoubleClickZoom: true, scrollwheel: false,
        draggable: false, streetViewControl: true,
        streetViewControlOptions: {
        position: google.maps.ControlPosition.BOTTOM_TOP
        }});

    v_marca = new google.maps.LatLng( log, lat);
    const punto = new google.maps.Marker({position: v_marca, map: v_mapa});

		let v_contenidoInfo = '<h4>'+titulo+'</h4>'
        + '<img src='+foto+' />'
        + '<p>'+titulo+'<br ><br >'+coment+'</p>'
        + '<a  href='+link+'>'+link+'</a>';
        
        let v_info = new google.maps.InfoWindow({content: v_contenidoInfo});

        google.maps.event.addListener( punto, 'click', function() {
        
            v_info.open(v_mapa, punto);
            });

    };

