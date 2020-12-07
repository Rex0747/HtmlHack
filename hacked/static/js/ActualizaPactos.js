window.onload = function(){
    desplHospital = document.getElementById('selhospC');
    desplDispositivo = document.getElementById('selDisp');
    submBoton = document.getElementById('subDisGfh');
    submBoton.addEventListener('click', ocultarDesplegables);


};

function ocultarDesplegables(){
    //document.write('CLICK');
    //alert('Entro');
    desplDispositivo.style.display = 'none';
    desplHospital.style.display = 'none';
    
    };

    function mostrarDesplegables(){
        //document.write('CLICK');
        desplDispositivo.style.display = 'block';
        desplHospital.style.display = 'block';
        
        };