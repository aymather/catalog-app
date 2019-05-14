const navSlide = () => {
    // Get Elements
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.right-nav');

    // Add event listener to burger element
    burger.addEventListener('click', () => {
        nav.style = 'transition: transform 1s ease';
        nav.classList.toggle('nav-active');
        burger.classList.toggle('toggle');
        burger.classList.toggle('burger-toggle');
    })
}

// Toggle Burger active
window.onresize = () => {
    const nav = $('.right-nav')[0];
    const burger = $('.burger')[0];
    if(window.innerWidth > 768 && nav.classList.contains('nav-active')){
        nav.classList.toggle('nav-active');
    }
    if(window.innerWidth > 768){
        nav.style.transition = 'none';
    }
    if(window.innerWidth >= 768 && burger.classList.contains('burger-toggle')){
        burger.classList.toggle('burger-toggle');
        burger.classList.toggle('toggle');
    }
}

// Listen for clicks on Tier categories
$('.click').click(function(e){
    console.log('hi');
    var dispObj = e.target.innerHTML;
    $('.chars').css('display', 'none');
    $(`.${dispObj}`).css('display', 'block');
    $('#chars-title')[0].innerHTML = `${dispObj} - Tier`;
})

navSlide();