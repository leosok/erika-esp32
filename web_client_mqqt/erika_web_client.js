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

var clientId = "Erika-Web";
var device_name = "Erika-Web-Device";
var topics = {
  show: "erika/1/show",
  print: "erika/1/show",
  status: "erika/1/status",
};

var status = 0;

// Create a client instance
client = new Paho.MQTT.Client(config.MQQT_SERVER, 80, clientId);

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// Last will
// var last_will = new Paho.MQTT.Message("last message");
// last_will.destinationName = "erika-print";

// connect the client

client.connect({
  onSuccess: onConnect,
  userName: config.MQQT_USERNAME,
  password: config.MQQT_PASSWORD,
  //willMessage: last_will,
});

// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("onConnect");
  client.subscribe(topics.show);
  client.subscribe(topics.status);
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:" + responseObject.errorMessage);
  }
}

// called when a message arrives
function onMessageArrived(message) {
  console.log(message.destinationName + ":" + message.payloadString);

  switch (message.destinationName) {
    case topics.status:
      status = message.payloadString;
      if (Number(status) == 2) {
        document.getElementById("status").innerHTML = "printing...";
      } else {
        document.getElementById("status").innerHTML = !!Number(status)
          ? "ready"
          : "offline";
      }

      console.log("status change:" + status);
      break;

    case topics.show:
      console.log("showning: " + message.payloadString);
      break;
  }
}
