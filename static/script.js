document.addEventListener('DOMContentLoaded', () => {
    // --- INTRO SEQUENCE LOGIC ---
    const introOverlay = document.getElementById('intro-overlay');
    const introSound = document.getElementById('intro-sound');

    // Attempt to play the sound automatically
    introSound.play().catch(error => {
        // This catch block handles browser autoplay restrictions.
        // On many browsers, audio can't play until the user clicks somewhere.
        console.warn("Audio autoplay was blocked. It will start after the first user interaction.", error);
        // We add a listener to play the sound on the first click if autoplay fails.
        document.body.addEventListener('click', () => introSound.play(), { once: true });
    });

    // Listen for when the sound has finished playing
    introSound.addEventListener('ended', () => {
        // Add the 'hidden' class to fade out the overlay
        introOverlay.classList.add('hidden');
    });
    
    // --- CHAT LOGIC ---
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    const addMessage = (text, sender) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        
        const p = document.createElement('p');
        p.textContent = text;
        messageElement.appendChild(p);
        
        chatBox.appendChild(messageElement);
        // Scroll to the bottom to see the new message
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    const sendMessage = async () => {
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;

        addMessage(userMessage, 'user');
        userInput.value = '';

        try {
            // Send the user's message to the Flask backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            const jarvisReply = data.reply;
            
            // Display Jarvis's reply
            addMessage(jarvisReply, 'jarvis');

        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, I seem to be having connection issues.', 'jarvis');
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});
