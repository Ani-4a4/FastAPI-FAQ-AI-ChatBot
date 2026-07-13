const chatButton = document.getElementById("chatButton");
const chatWindow = document.getElementById("chatWindow");
const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");

chatButton.onclick = () => {
    chatWindow.style.display =
        chatWindow.style.display === "flex" ? "none" : "flex";
};

sendButton.onclick = sendMessage;

async function sendMessage() {

    const question = input.value.trim();

    if (!question) return;

    messages.innerHTML += `<p><b>You:</b> ${question}</p>`;

    input.value = "";

    try{
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: question,
                business_id: "demo-vegetable-wholesale"
            })
        });
 
        const data = await response.json();
        // Fall back to data.detail so backend errors are visible instead of "undefined".
        const answer = data.response || data.detail || "Something went wrong.";
        messages.innerHTML += `<p><b>Bot:</b> ${answer}</p>`;
    } catch (err) {
        messages.innerHTML += `<p><b>Bot:</b> Couldn't reach the server. Is it running?</p>`;
    }
 
    messages.scrollTop = messages.scrollHeight;
}