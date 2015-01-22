$(document).ready(function() {
    $('#fullpage').fullpage({
        //Navigation
        anchors: ['1', '2', '3', '4','5', '6', '7', '8', '9', 'lastpage'],
        navigation: true,
        navigationPosition: 'right',
        slidesNavigation: true,

        //Scrolling
        loopTop: true,
        loopBottom: true,
        scrollingSpeed: 500,
        // scrollBar: true,
        easing: 'easeInQuart',
        touchSensitivity: 15,
    });
});