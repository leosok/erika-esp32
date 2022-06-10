// erika_web_client.js
// Conntects to a MQQT-Broker for communication with erika

// SETTINGS //
// Please uncomment or write to "mqqr_config.js", to store keys outside VCS //

// const config = {
//     MQQT_SERVER = "",
//     MQQT_USERNAME = "",
//     MQQT_PASSWORD = ""
//   }

/////////////

function send_mqtt_msg(client, topic) {
    text = document.getElementById("erika_text").value.trim();
    message = new Paho.MQTT.Message(text);
    message.destinationName = topic;
    client.send(message);
  }
  
  function download(textarea_id) {
    var text = document.getElementById(textarea_id).value;
    text = text.replace(/\n/g, "\r\n"); // To retain the Line breaks.
    var blob = new Blob([text], { type: "text/plain" });
    var anchor = document.createElement("a");
    anchor.download = "my-filename.txt";
    anchor.href = window.URL.createObjectURL(blob);
    anchor.target = "_blank";
    anchor.style.display = "none"; // just to be safe!
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
  }
  
  function typeInTextarea(newText, el = document.activeElement) {
    const [start, end] = [el.selectionStart, el.selectionEnd];
    el.setRangeText(newText, start, end, 'end');
  }
  
  function removePreviousCharacter(el = document.activeElement) {
    const [start, end] = [el.selectionStart, el.selectionEnd];
    el.setRangeText('', start-1, end, 'end');
  }
  
  function add_text_to_textarea(textarea, text){
    // Adds Text(Char) and scrolls down
  
    typeInTextarea(text, textarea)
    if (textarea.selectionEnd >= textarea.textLength) {
      // If we are at the buttom, scroll down for better text view
      textarea.scrollTop = textarea.scrollHeight
    } 
  }
  
  
  var random_str =
    Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15);
  var clientId = "Erika-Web-Receiver" + random_str;
  var device_name = "Erika-Web-Receiver" + random_str;
  var topics = {
    keystrokes: config.topic_keycast,
    status: config.topic_status
  };
  
  var status = 0;
  
  // Create a client instance
  client = new Paho.MQTT.Client(config.MQQT_SERVER, 80, clientId);
  
  // set callback handlers
  client.onConnectionLost = onConnectionLost;
  client.onMessageArrived = onMessageArrived;
  doConnect();
  
  // Last will
  // var last_will = new Paho.MQTT.Message("last message");
  // last_will.destinationName = "erika-print";
  
  // connect the client
  
  function doConnect() {
    client.connect({
      onSuccess: onConnect,
      userName: config.MQQT_USERNAME,
      password: config.MQQT_PASSWORD,
      //willMessage: last_will,
    });
  }
  
  // called when the client connects
  function onConnect() {
    // Once a connection has been made, make a subscription and send a message.
    console.log("onConnect");
    console.log("subscribing: "+topics.keystrokes)
    client.subscribe(topics.status);
    client.subscribe(topics.keystrokes);
    // disable reconnection timer
    if (window.reconnection_timer) {
      clearInterval(window.reconnection_timer);
    }
  }
  
  // called when the client loses its connection
  function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
      console.log("onConnectionLost:" + responseObject.errorMessage);
    }
    // try reconnecting
    console.log("Trying to reconnect...:");
    doConnect();
    // set a timer to try reconnecting
    window.reconnection_timer = setInterval(doConnect(), 5000);
  }
  
  // called when a message arrives
  function onMessageArrived(message) {
    //console.log(message.destinationName + ":" + message.payloadString);
    var print_button = document.querySelector("#print_button");
  
    switch (message.destinationName) {
      case topics.status:
        status = message.payloadString;
        if (Number(status) == 2) {
          document.getElementById("status").innerHTML = "printing...";
          print_button.disabled = true;
        } else {
          document.getElementById("status").innerHTML = !!Number(status)
            ? "ready"
            : "offline";
          print_button.disabled = false;
  
          document.getElementById("erika_text").placeholder = !!Number(status)
            ? "Ready to receive!"
            : "Waiting...";
        }
  
        console.log("status change:" + status);
        break;
  
      case topics.show:
        console.log("showning: " + message.payloadString);
        break;
  
      case topics.keystrokes:
        var main_textarea = document.getElementById("erika_text");
        next_char = message.payloadString;
        if (next_char == "DEL") {
          removePreviousCharacter(main_textarea)
        } else {
         add_text_to_textarea(main_textarea, next_char)
        }
  
        //console.log("")
        break;
    }
  }
  