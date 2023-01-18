// Get operators from menu and contents from page
let menuOperators = document.querySelectorAll('.operator');
let contentBlocks = [...document.querySelectorAll('.content')];

// On menu operator click call a function
[...menuOperators].forEach((operator) => {
   operator.addEventListener('click', () => {
      //  Get menu operator text which matches content class
      let className = operator.textContent.toLowerCase();
      contentBlocks.forEach((div) => {
          // Add or remove class based on current choice
          if (div.classList.contains(className)) {
              div.classList.remove('disabled');
          } else {
              div.classList.add('disabled');
          }
      });
   });
});
