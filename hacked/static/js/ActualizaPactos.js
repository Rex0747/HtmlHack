

$(document).ready(function(){

    $(".loader").fadeOut("slow");
    $('#Htitulo').text('Modificar pactos');
    boton = document.getElementById('boton');
    //boton.style.display = 'none';
    tabla = document.getElementById('tabla')//.style.display = 'none';

    despGfh = document.getElementById('selDisp');
    despGfh.style.display = 'none';

   // boton.addEventListener('click',mostraTabla);
    despHospital = document.getElementById('selhospC');
    despHospital.addEventListener('change', desplHospital);


    despGfh.addEventListener('change', desplGfh);
});

function desplHospital(){
    despGfh.style.display = 'block';
};

function desplGfh(){
    boton.style.display = 'block';
    tabla.style.display = 'block';
};



function mostrarTabla(){
    document.getElementById('tabla').style.display = 'block';
    
}