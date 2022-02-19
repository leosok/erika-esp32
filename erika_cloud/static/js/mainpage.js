

document.addEventListener("DOMContentLoaded", function(event) {
    setInterval(reload_online_typewriters, 5000)
});

function send_text_to_printer() {
            text = document.getElementById("erika_text").value.trim();

            var select = document.getElementById('typewriters_online');
            var uuid = select.options[select.selectedIndex].value;

            // Sending and receiving data in JSON format using POST method
            if (uuid != 0) {
                var xhr = new XMLHttpRequest();
                var url = "/typewriter/" + uuid + "/print";

                console.log("printig to " + url)

                xhr.open("POST", url, true);
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        //console.log("Success: " + xhr.responseText);
                    }
                };
                var data = JSON.stringify({"body": text});
                xhr.send(data);
            }
        }

function reload_online_typewriters(){
    var xhr = new XMLHttpRequest();
        var url = "/typewriters/online";

        xhr.open("GET", url, true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log("Success: " + xhr.responseText);
                // Replace content of select:
                document.getElementById("typewriters_online")
                    .outerHTML = xhr.responseText
            }
        };
        xhr.send(null);
    }
