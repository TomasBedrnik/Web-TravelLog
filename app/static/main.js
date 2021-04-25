function hide_more_labels() {
    let descriptions = document.getElementsByClassName("activity_description");
    for (let i = 0; i < descriptions.length; i++) {
        if(descriptions[i].getElementsByClassName("activity_description_inner")[0].scrollHeight ===
            descriptions[i].getElementsByClassName("activity_description_inner")[0].offsetHeight) {
            descriptions[i].getElementsByClassName("more_label")[0].style.visibility = 'hidden'
        }
    }
}