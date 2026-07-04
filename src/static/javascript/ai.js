function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

const csrftoken = getCookie("csrftoken");





async function rewriteWithAi(textareaId, counterId) {
    const text = document.getElementById(textareaId).value;

    const response = await fetch("/ai/rewrite/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrftoken
        },
        body: new URLSearchParams({
            text: text
        })
    });

    const data = await response.json();

    if (data.result) {
        document.getElementById(textareaId).value = data.result;
        const counters = document.getElementsByClassName(counterId);

        for (let counter of counters) {
            counter.innerHTML = data.remaining;
        }
    }

    if (data.error) {
        id = `error_${textareaId}`
        error = document.getElementById(id)
        error.innerHTML = data.error
    }
}