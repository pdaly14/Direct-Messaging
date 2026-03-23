console.log("app.js loaded");

function sayHi() {
  console.log("HI");
  document.getElementById("output").innerText = "JavaScript works!";
}

// Add this to your app.js
const chatBox = document.getElementById('chat-box');
chatBox.scrollTop = chatBox.scrollHeight;



function fetchMessages() {
  fetch("/messages")
    .then(response => response.json())
    .then(data => {
      const chatBox = document.getElementById("chat-box");
      chatBox.innerHTML = "";

      data.forEach(msg => {
        const p = document.createElement("p");
        // Use a standard /profile/ URL string
        p.innerHTML = `<strong><a href="/profile/${msg.user}">${msg.user}</a>:</strong> ${msg.text} <em>(${msg.time})</em>`;

        chatBox.appendChild(p);
      });
    });
}

function secretFunction() {
  console.log("This is a secret function!");
  document.getElementById("67").innerText = "secret 67";
}


console.log(username);
setInterval(fetchMessages, 2000);
fetchMessages();