window.onload = function() {
$(".loader").hide().fadeIn("slow");
boton = document.getElementById('boton2');
boton.disabled = true;

//alert("Entro solo");

}


function enableBoton(){
    boton.disabled = false
   // alert("Has pinchao");
    }