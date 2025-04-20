// Define chatBox globally
const chatBox = document.getElementById('chat-box');

document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input'); 

    // First welcome message
    const message1 = document.createElement('div');
    message1.className = 'chat-message bot';
    message1.textContent = "Hello!👋👋👋";
    chatBox.appendChild(message1);

    // Second welcome message
    const message2 = document.createElement('div');
    message2.className = 'chat-message bot';
    message2.textContent = "Happy to help you create the best Conversational AI experience for your shopping!";
    chatBox.appendChild(message2);

    // Third welcome message
    const message3 = document.createElement('div');
    message3.className = 'chat-message bot';
    message3.textContent = "Welcome! I am VROOMbot! How can I assist you today?";
    chatBox.appendChild(message3);

    // Add "Let's get started!" button
    const startButton = document.createElement('button');
    startButton.className = 'start-button';
    startButton.textContent = "Let's get started!";
    startButton.onclick = () => {
        // Simulate user message
        const userMessage = document.createElement('div');
        userMessage.className = 'chat-message user';
        userMessage.textContent = "Let's get started!";
        chatBox.appendChild(userMessage);

        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;

        // Simulate bot response
        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message bot';
        botMessage.textContent = "Here's how you can get started:";
        chatBox.appendChild(botMessage);

        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;

        // Hide the "Let's get started!" button
        startButton.style.display = 'none';

        // Add options as buttons
        const options = ["List Vehicles", "Filter Vehicles", "Compare Vehicles", "Let's Chat"];
        const optionsContainer = document.createElement('div');
        optionsContainer.className = 'options-container';

        options.forEach(option => {
            const optionButton = document.createElement('button');
            optionButton.className = 'option-button';
            optionButton.textContent = option;
            optionButton.onclick = () => {
                // Simulate user selecting an option
                const userOption = document.createElement('div');
                userOption.className = 'chat-message user';
                userOption.textContent = option;
                chatBox.appendChild(userOption);

                // Scroll to the bottom of the chat box
                chatBox.scrollTop = chatBox.scrollHeight;

                // Add loading indicator
                const loadingIndicator = document.createElement('div');
                loadingIndicator.className = 'loading-indicator';
                loadingIndicator.textContent = 'Typing...';
                chatBox.appendChild(loadingIndicator);

                // Handle "List Vehicles" query
                if (option === "List Vehicles") {
                    fetch('/get_vehicle_table/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken(),
                        },
                        body: JSON.stringify({ query: "List Vehicles" }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server Response:', data);
                        chatBox.removeChild(loadingIndicator);
                
                        // Update the call to renderVehicleTable
                        if (data.status === "success" && data.vehicles) {
                            renderVehicleTable(chatBox, data.vehicles);
                        } else {
                            appendBotMessage(data.message || 'No vehicles found.');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        chatBox.removeChild(loadingIndicator);
                        appendBotMessage('An error occurred. Please try again later.');
                    });
                } else if (option === "Let's Chat") {
                    userInput.focus(); 
                    loadingIndicator.remove(); 
                } else {
                    const botResponse = document.createElement('div');
                    botResponse.className = 'chat-message bot';
                    botResponse.textContent = `You selected: ${option}`;
                    chatBox.appendChild(botResponse);
                }

                // Scroll to the bottom of the chat box
                chatBox.scrollTop = chatBox.scrollHeight;

                // Hide the options container
                optionsContainer.style.display = 'none';
            };
            optionsContainer.appendChild(optionButton);
        });

        chatBox.appendChild(optionsContainer);
        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    };
    chatBox.appendChild(startButton);
});


// Update the renderVehicleTable function
const renderVehicleTable = (chatBox, vehicles) => {
    const table = document.createElement('table');
    table.className = 'vehicle-table';

    // Create table header
    const headerRow = document.createElement('tr');
    ['ID', 'Brand', 'Model', 'Year', 'Fuel Type', 'Price'].forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Populate table rows with vehicle data
    vehicles.forEach(vehicle => {
        const row = document.createElement('tr');
        ['ID', 'Brand', 'Model', 'Year', 'Fuel Type', 'Price'].forEach(key => {
            const td = document.createElement('td');
            td.textContent = vehicle[key] || 'N/A';
            row.appendChild(td);
        });
        table.appendChild(row);
    });

    // Append the table to the chat box
    const botResponse = document.createElement('div');
    botResponse.className = 'chat-message bot';
    botResponse.appendChild(table);
    chatBox.appendChild(botResponse);
    chatBox.scrollTop = chatBox.scrollHeight;
};

// Function to append a bot message
const appendBotMessage = (message) => {
    const botMessage = document.createElement('div');
    botMessage.className = 'chat-message bot';
    botMessage.textContent = message;
    chatBox.appendChild(botMessage);
    chatBox.scrollTop = chatBox.scrollHeight;
};


// Function to get the CSRF token from cookies
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}

function sendMessage() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (message) {
        // Display user message
        const userMessage = document.createElement('div');
        userMessage.className = 'chat-message user';
        userMessage.textContent = message;
        chatBox.appendChild(userMessage);

        // Clear input field
        userInput.value = '';

        // Add loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading-indicator';
        loadingIndicator.textContent = 'Typing...';
        chatBox.appendChild(loadingIndicator);

        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;

        // Send the message to the server
        fetch('/query/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), 
            },
            body: JSON.stringify({ query: message }),
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            chatBox.removeChild(loadingIndicator);

            // Display bot response
            const botMessage = document.createElement('div');
            botMessage.className = 'chat-message bot';
            botMessage.textContent = data.response || 'Sorry, I could not process your request.';
            chatBox.appendChild(botMessage);

            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            const botMessage = document.createElement('div');
            botMessage.className = 'chat-message bot';
            botMessage.textContent = 'An error occurred. Please try again later.';
            chatBox.appendChild(botMessage);
        });
    }
}