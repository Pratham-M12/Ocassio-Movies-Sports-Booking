document.addEventListener("DOMContentLoaded", function () {
    fetch("http://127.0.0.1:8000/api/home/")
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").innerText = data.message;
        })
        .catch(error => console.error("Error:", error));
});
