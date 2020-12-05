

window.onload = function(){
    //selectorHospital = document.getElementById('contHospCod');
    //selectorHospital.addEventListener('change', contHospCod );

    selinput = document.getElementsByTagName('hhosp',contHospCod)
    selinput.addEventListener('change', contHospCod );

};

function contHospCod(e){
    console.log(e.target);
    getElementById('hhosp').value = e.target
    
}