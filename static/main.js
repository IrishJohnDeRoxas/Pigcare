 // get all the li elements in the sidebar-links class
 var liElements = document.querySelectorAll(".sidebar-links li");
 var main = document.querySelector('main');
 var sidebar =  document.getElementById('sidebar');
 var closeBtn = document.getElementById('sidebar-close-btn');

 var scrape_button = document.getElementById('scrape-button')
 
 // apply a function to each li element
 liElements.forEach(function(li) {
   // get the a element inside the li element
   var a = li.querySelector("a");
   // check if the a element has a class active
   if (a.classList.contains("active")) {
     // change the li design as desired
     li.classList.add('active')
   }
 });
 
 if(closeBtn){
   closeBtn.addEventListener('click', ()=>{
     sidebar.classList.toggle('hide');
     closeBtn.classList.toggle('collapse');
     main.classList.toggle('expand');
 })
 }


 var alert = document.querySelector('.alert')
 if(alert){
     window.onload = function(){
         alert.classList.toggle('hide')
     }
 }

 var modals = document.getElementsByClassName('modal');
 var close = document.getElementsByClassName('close');
 for (var i = 0; i < modals.length; i++) {
   modals[i].addEventListener('click', function(event) {
     if (event.target == this) {
       this.classList.remove('show');
     }
   });
 }

 for (var i = 0; i < close.length; i++) {
  close[i].addEventListener('click', ()=> {
     this.classList.remove('show');
   });
 }

function confirmDelete(item) {
  var modal = document.getElementById('delete-modal-' + item);
  modal.classList.toggle('show')    
}

var option_1 = document.querySelector('.option-1')
var option_2 = document.querySelector('.option-2')
var option_1_value = document.querySelector('.option-1-value')
var option_2_value = document.getElementById('.option-2-value')


if (option_1){
  option_1.addEventListener('click',()=>{
    option_1.classList.remove('active')
    option_2.classList.remove('active')
    option_1_value.classList.remove('hide')
    option_2_value.classList.remove('show')
  })
}

  if (option_2){
    option_2.addEventListener('click',()=>{
      option_1.classList.add('active')
      option_2.classList.add('active')
      option_1_value.classList.add('hide')
      option_2_value.classList.add('show')
    })
  }



