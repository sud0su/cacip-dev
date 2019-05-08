jQuery(function ($) {

    'use strict';

    // -------------------------------------------------------------
    // Preloader
    // -------------------------------------------------------------
    (function () {
        $('#status').fadeOut();
        $('#preloader').delay(200).fadeOut('slow');
    }());



    // ------------------------------------------------------------------
    // sticky menu
    // ------------------------------------------------------------------

     $(window).scroll(function() {
        if ($(this).scrollTop() >= 50) {
            $('nav.navbar').addClass('sticky-nav');
        }
        else {
            $('nav.navbar').removeClass('sticky-nav');
        }
    });



    // -------------------------------------------------------------
    // mobile menu
    // -------------------------------------------------------------
    (function () {
        $('button.navbar-toggle').ucOffCanvasMenu({
        documentWrapper: '#main-wrapper',
        contentWrapper : '.content-wrapper',
        position       : 'uc-offcanvas-left',    // class name
        // opener         : 'st-menu-open',            // class name
        effect         : 'slide-along',             // class name
        closeButton    : '#uc-mobile-menu-close-btn',
        menuWrapper    : '.uc-mobile-menu',                 // class name below-pusher
        documentPusher : '.uc-mobile-menu-pusher'
        });
    }());




    // -------------------------------------------------------------
    // tooltip
    // -------------------------------------------------------------

    (function () {

        $('[data-toggle="tooltip"]').tooltip()

    }());




    // ------------------------------------------------------------------
    // jQuery for back to Top
    // ------------------------------------------------------------------
    (function(){

          $('body').append('<div id="toTop"><i class="fa fa-angle-up"></i></div>');

            $(window).scroll(function () {
                if ($(this).scrollTop() != 0) {
                    $('#toTop').fadeIn();
                } else {
                    $('#toTop').fadeOut();
                }
            }); 

        $('#toTop').on('click',function(){
            $("html, body").animate({ scrollTop: 0 }, 600);
            return false;
        });

    }());

    // ------------------------------------------------------------------
    // jQuery for Carousel Swipe
    // ------------------------------------------------------------------
    (function(){
        $('.carousel').bcSwipe({ threshold: 50 });
    }());

}); // JQuery end


$(document).on('click', '.m-menu .dropdown-menu', function(e) {
  e.stopPropagation();
})

// ------------------------------------------------------------------
// Fixing Menu on Interactive Maps
// ------------------------------------------------------------------
$(window).load(function(){
    if($("#ext-comp-1012").length){
        console.log('ada');
        $("#wrap").append($("#ext-comp-1012"));
    }
});