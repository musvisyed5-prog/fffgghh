function changeDisablity(text, inputID, buttonID) {
    console.log(text, inputID, buttonID)
    let input = document.getElementById(inputID);
    let button = document.getElementById(buttonID);

    if (input && button) {
        if (input.value.trim() === text) {
            button.disabled = false;
        } else {
            button.disabled = true;
        }
    }
}