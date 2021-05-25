function hide_more_labels() {
    let descriptions = document.getElementsByClassName("activity_description");
    for (let i = 0; i < descriptions.length; i++) {
        if(descriptions[i].getElementsByClassName("activity_description_inner").length > 0) {
            if(descriptions[i].getElementsByClassName("activity_description_inner")[0].scrollHeight ===
                descriptions[i].getElementsByClassName("activity_description_inner")[0].offsetHeight) {
                descriptions[i].getElementsByClassName("more_label")[0].style.visibility = 'hidden'
            }
        }
    }

    let menu = document.getElementById("a")
    //Swipe side menu on map:
    menu.addEventListener('touchstart', handleTouchStart, false);
    menu.addEventListener('touchmove', handleTouchMove, false);

    var xDown = null;
    var yDown = null;

    function getTouches(evt) {
      return evt.touches ||             // browser API
             evt.originalEvent.touches; // jQuery
    }

    function handleTouchStart(evt) {
        const firstTouch = getTouches(evt)[0];
        xDown = firstTouch.clientX;
        yDown = firstTouch.clientY;
    };

    function handleTouchMove(evt) {
        if ( ! xDown || ! yDown ) {
            return;
        }

        var xUp = evt.touches[0].clientX;
        var yUp = evt.touches[0].clientY;

        var xDiff = xDown - xUp;
        var yDiff = yDown - yUp;

        if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
            if ( xDiff > 0 ) {
                /* left swipe */
                window.location.href = "#a"
            } else {
                /* right swipe */
                window.location.href = "#"
            }
        } else {
            if ( yDiff > 0 ) {
                /* up swipe */
            } else {
                /* down swipe */
            }
        }
        /* reset values */
        xDown = null;
        yDown = null;
    };
}