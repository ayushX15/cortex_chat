const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// Optimized message adding with animation
function addMessage(text, isUser) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    messageDiv.classList.add(isUser ? "user-message" : "bot-message");
    
    // Add typing indicator for bot messages
    if (!isUser) {
        const loadingDiv = document.createElement("div");
        loadingDiv.classList.add("loading");
        messageDiv.appendChild(loadingDiv);
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Simulate typing effect for better UX
        let i = 0;
        const typingInterval = setInterval(() => {
            if (i < text.length) {
                if (loadingDiv.parentNode) {
                    loadingDiv.remove();
                }
                messageDiv.textContent = text.substring(0, i + 1);
                i++;
                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                clearInterval(typingInterval);
            }
        }, 20); // Adjust typing speed here
        
        return;
    }
    
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Optimized AI response fetching
async function getAIResponse(prompt) {
    try {
        const startTime = performance.now();
        
        const response = await fetch("http://localhost:11434/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: "llama3", // Change if using another model
                prompt: prompt,
                stream: false,
            }),
        });
        
        const data = await response.json();
        const endTime = performance.now();
        console.log(`Response time: ${(endTime - startTime).toFixed(2)}ms`);
        
        return data.response;
    } catch (error) {
        console.error("Error:", error);
        return "Sorry, I couldn't process your request. Please try again.";
    }
}

// Handle sending messages
async function sendMessage() {
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    addMessage(userMessage, true);
    userInput.value = "";
    userInput.focus();

    const aiResponse = await getAIResponse(userMessage);
    addMessage(aiResponse, false);
}

// Event listeners
sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// Auto-focus input on page load
window.addEventListener("DOMContentLoaded", () => {
    userInput.focus();
});