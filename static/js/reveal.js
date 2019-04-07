// Set so that seeing the same place twice
// doesn't re-reveal
ScrollReveal({ reset: false });

// Base settings
var base = {
    distance: '20%',
    duration: '1000'
}

// Select all elements with the 'slide' prefix
var elements = document.querySelectorAll('[class^=slide]');

// Create a Regular expression for matching elements
var exp = new RegExp('slide*');

// Loop through list of elements
for (i in elements) {

    // Loop through each class type (looking for delays)
    var x = elements[i].classList;
    for (c in x){

        // If element matches the regex
        if (exp.exec(x[c])){

            // Split the class name into parts
            var classSplit = x[c].split('-');

            // Parse direction
            var direction = classSplit[1];

            // Parse for delay if it exists
            // Default: 0
            if (classSplit[2]) {
                var delay = classSplit[2];
            } else {
                var delay = '0';
            };

            // Merge settings with base
            var settings = {
                ...base,
                origin: direction,
                delay: (parseInt(delay) * 1000)
            };

            // Apply ScrollReveal to matching elements
            var ele = document.querySelectorAll(`.${x[c]}`);
            ScrollReveal().reveal(ele, settings);
        }
    }
}