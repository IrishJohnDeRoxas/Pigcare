 // get all the li elements in the sidebar-links class
 var liElements = document.querySelectorAll(".sidebar-links li");
 var main = document.querySelector('main');
 var sidebar =  document.getElementById('sidebar');
 var closeBtn = document.getElementById('sidebar-close-btn');

 var modal = document.querySelector('.modal')
 var scrape_button = document.getElementById('scrape-button')

 
 // apply a function to each li element
 liElements.forEach(function(li) {
   // get the a element inside the li element
   var a = li.querySelector("a");
   // check if the a element has a class active
   if (a.classList.contains("active")) {
     // change the li design as desired
     // for example, change the background color to green
     li.classList.add('active')
   }
 });
 
 
 closeBtn.addEventListener('click', ()=>{
     sidebar.classList.toggle('close');
     closeBtn.classList.toggle('collapse');
     main.classList.toggle('expand');
 })

 scrape_button.addEventListener('click', ()=>{
    modal.show()
 })