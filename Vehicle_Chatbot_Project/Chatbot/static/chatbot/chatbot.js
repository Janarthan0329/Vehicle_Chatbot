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

    // Fourth welcome message
    const message4 = document.createElement('div');
    message4.className = 'chat-message bot';
    message4.innerHTML = "Just type <a href='#' id='options-link' style='color: yellow; font-size: 1.2em; text-decoration: none;'>'Options'</a> anywhere and Click 'Send' button to access easy options to get started! <br> Or you can type <a href='#' style='color: yellow; font-size: 1.2em; text-decoration: none;'>'start over'</a> anywhere and Click 'Send' button to reset the conversation.";
    chatBox.appendChild(message4);

    // Add event listener to the hyperlink
    const optionsLink = document.getElementById('options-link');
    optionsLink.addEventListener('click', (event) => {
        event.preventDefault(); 
        const startButton = document.querySelector('.start-button');
        if (startButton && startButton.onclick) {
            startButton.onclick(); 
        }
    });

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

                // Clear previous inputs and reset variables
                userInput.value = '';
                

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
                } else if (option === "Filter Vehicles") {
                    // Define the filter fields and filters globally
                    const filterFields = ['brand', 'model', 'fuel_type', 'transmission'];
                    const filters = {};
                    let currentFilterIndex = 0;
                
                    // Define the event listener function globally
                    const handleKeyPress = (e) => {
                        if (e.key === 'Enter') {
                            const value = userInput.value.trim();
                            userInput.value = '';
                            if (value) {
                                const field = filterFields[currentFilterIndex];
                                filters[field] = value;
                    
                                // Display user input
                                const userMessage = document.createElement('div');
                                userMessage.className = 'chat-message user';
                                userMessage.textContent = value;
                                chatBox.appendChild(userMessage);
                    
                                // Move to the next filter field
                                askForFilter(currentFilterIndex + 1);
                            }
                        }
                    };
                
                    // Function to ask for filter inputs
                    const askForFilter = (index) => {
                        currentFilterIndex = index;
                
                        if (index >= filterFields.length) {
                            console.log('Filters being sent:', filters);
                            fetch('/filter/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCSRFToken(),
                                },
                                body: JSON.stringify({ filters }),
                            })
                            .then(response => response.json())
                            .then(data => {
                                console.log('Server Response:', data);
                                chatBox.removeChild(loadingIndicator);
                        
                                if (data.status === "success" && data.response) {
                                    const vehicles = data.response;
                        
                                    if (typeof vehicles === "string") {
                                        const botResponse = document.createElement('div');
                                        botResponse.className = 'chat-message bot';
                                        botResponse.textContent = vehicles;
                                        chatBox.appendChild(botResponse);
                                    } else {
                                        const table = document.createElement('table');
                                        table.className = 'vehicle-table';
                        
                                        const headerRow = document.createElement('tr');
                                        ['Brand', 'Model','Type', 'Category', 'Fuel Type', 'Transmission', 'Year', 'Mileage', 'Specification'].forEach(header => {
                                            const th = document.createElement('th');
                                            th.textContent = header;
                                            headerRow.appendChild(th);
                                        });
                                        table.appendChild(headerRow);
                        
                                        vehicles.forEach(vehicle => {
                                            const row = document.createElement('tr');
                                            ['brand', 'model', 'type', 'category', 'fuel_type', 'transmission', 'year', 'mileage'].forEach(key => {
                                                const td = document.createElement('td');
                                                td.textContent = vehicle[key] || 'N/A';
                                                row.appendChild(td);
                                            });

                                            // Add "Specification" button
                                            const specButtonCell = document.createElement('td');
                                            const specButton = document.createElement('button');
                                            specButton.textContent = 'Spec';
                                            specButton.className = 'spec-button';
                                            specButton.onclick = () => {
                                                // Fetch and display specifications for the selected vehicle
                                                fetch(`/vehicle_specifications/${vehicle.id}/`, {
                                                    method: 'GET',
                                                    headers: {
                                                        'Content-Type': 'application/json',
                                                    },
                                                })
                                                .then(response => response.json())
                                                .then(specData => {
                                                    if (specData.status === "success") {
                                                        // Populate the modal with vehicle details
                                                        const modalDetails = document.getElementById('modal-details');
                                                        modalDetails.innerHTML = `
                                                            Specifications for ${vehicle.brand} ${vehicle.model}:<br>
                                                            ${Object.entries(specData.specifications)
                                                                .map(([key, value]) => `<p>${key}: ${value}</p>`)
                                                                .join('')}
                                                        `;

                                                        // Display the modal
                                                        const modal = document.getElementById('vehicle-modal');
                                                        modal.style.display = 'block';
                                                    } else {
                                                        appendBotMessage('Unable to fetch specifications.');
                                                    }
                                                })
                                                .catch(error => {
                                                    console.error('Error fetching specifications:', error);
                                                    appendBotMessage('An error occurred while fetching specifications.');
                                                });
                                            };
                                            specButtonCell.appendChild(specButton);
                                            row.appendChild(specButtonCell);

                                            table.appendChild(row);
                                        });

                                        const botResponse = document.createElement('div');
                                        botResponse.className = 'chat-message bot';
                                        botResponse.appendChild(table);
                                        chatBox.appendChild(botResponse);
                                    }
                                } else {
                                    const botResponse = document.createElement('div');
                                    botResponse.className = 'chat-message bot';
                                    botResponse.textContent = 'No vehicles match the filters.';
                                    chatBox.appendChild(botResponse);
                                }

                                chatBox.scrollTop = chatBox.scrollHeight;

                                // Reset filters after the workflow is complete
                                Object.keys(filters).forEach(key => delete filters[key]);
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                const botResponse = document.createElement('div');
                                botResponse.className = 'chat-message bot';
                                botResponse.textContent = 'An error occurred. Please try again later.';
                                chatBox.appendChild(botResponse);
                            });
                            return;
                        }
                
                        // Close the modal when the close button is clicked
                        const modal = document.getElementById('vehicle-modal');
                        const closeButton = document.querySelector('.close-button');

                        closeButton.onclick = () => {
                            modal.style.display = 'none';
                        };

                        // Close the modal when clicking outside of it
                        window.onclick = (event) => {
                            if (event.target === modal) {
                                modal.style.display = 'none';
                            }
                        };

                        // Ask for the next filter field
                        const field = filterFields[index];
                        const botResponse = document.createElement('div');
                        botResponse.className = 'chat-message bot';
                        botResponse.textContent = `Please enter a value for ${field}: & Click the "Enter" key on your keyboard`;
                        chatBox.appendChild(botResponse);
                
                        // Scroll to the bottom of the chat box
                        chatBox.scrollTop = chatBox.scrollHeight;

                        // Remove any existing event listener
                        userInput.removeEventListener('keypress', handleKeyPress);
                
                        // Add the new event listener
                        userInput.addEventListener('keypress', handleKeyPress);
                    };
                
                    // Trigger the "Filter Vehicles" functionality
                    const startFilterVehicles = () => {
                        // Reset filters and index
                        Object.keys(filters).forEach(key => delete filters[key]);
                        currentFilterIndex = 0;
                
                        // Start asking for filters
                        askForFilter(0);
                    };
                
                    // Start the filtering process
                    startFilterVehicles();
                } else if (option === "Compare Vehicles") {
                    // Prompt user to enter details for two vehicles
                    const vehicleDetails = [];
                    let currentVehicleIndex = 0;
                
                    const askForVehicleDetails = () => {
                        if (currentVehicleIndex >= 2) {
                            // Send the details to the backend for comparison
                            fetch('/compare_vehicles/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCSRFToken(),
                                },
                                body: JSON.stringify({
                                    vehicle1: vehicleDetails[0],
                                    vehicle2: vehicleDetails[1]
                                }),
                            })
                            .then(response => response.json())
                            .then(data => {
                                chatBox.removeChild(loadingIndicator);
                
                                if (data.status === "success") {
                                    const comparison = data.comparison;
                
                                    // Generate vehicle names for column headers
                                    const vehicle1Name = `${vehicleDetails[0].brand} ${vehicleDetails[0].model} ${vehicleDetails[0].type} (${vehicleDetails[0].category || 'N/A'})`;
                                    const vehicle2Name = `${vehicleDetails[1].brand} ${vehicleDetails[1].model} ${vehicleDetails[1].type} (${vehicleDetails[1].category || 'N/A'})`;

                                    // Create a table for comparison
                                    const table = document.createElement('table');
                                    table.className = 'vehicle-table';
                
                                    // Create table header
                                    const headerRow = document.createElement('tr');
                                    ['Aspect', `Vehicle 1: ${vehicle1Name}`, 'Vehicle 2: ' + vehicle2Name].forEach(header => {
                                        const th = document.createElement('th');
                                        th.textContent = header;
                                        headerRow.appendChild(th);
                                    });
                                    table.appendChild(headerRow);
                
                                    // Populate table rows with comparison data
                                    comparison.Aspect.forEach((aspect, index) => {
                                        const tr = document.createElement('tr');
                                        const aspectCell = document.createElement('td');
                                        aspectCell.textContent = aspect;
                                        tr.appendChild(aspectCell);
                
                                        const vehicle1Cell = document.createElement('td');
                                        vehicle1Cell.textContent = comparison["Vehicle 1"][index] || 'N/A';
                                        tr.appendChild(vehicle1Cell);
                
                                        const vehicle2Cell = document.createElement('td');
                                        vehicle2Cell.textContent = comparison["Vehicle 2"][index] || 'N/A';
                                        tr.appendChild(vehicle2Cell);
                
                                        table.appendChild(tr);
                                    });
                
                                    // Append the table to the chat box
                                    const botResponse = document.createElement('div');
                                    botResponse.className = 'chat-message bot';
                                    botResponse.appendChild(table);
                                    chatBox.appendChild(botResponse);

                                    // Add "Price Recommendations" button below the table
                                    const priceButton = document.createElement('button');
                                    priceButton.className = 'option-button';
                                    priceButton.textContent = "Price Recommendations";
                                    priceButton.onclick = () => {
                                        promptForVehicleChoice();

                                        chatBox.scrollTop = chatBox.scrollHeight;
                                    };

                                    chatBox.appendChild(priceButton);
                                } else {
                                    appendBotMessage(data.message || 'An error occurred while comparing vehicles.');
                                }
                
                                chatBox.scrollTop = chatBox.scrollHeight;
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                chatBox.removeChild(loadingIndicator);
                                appendBotMessage('An error occurred. Please try again later.');
                            });
                            return;
                        }
                
                        // Ask for details of the next vehicle
                        const botMessage = document.createElement('div');
                        botMessage.className = 'chat-message bot';
                        botMessage.textContent = `Please enter details for Vehicle ${currentVehicleIndex + 1} (brand, model, type): & Click the "Enter" key on your keyboard`;
                        chatBox.appendChild(botMessage);
                
                        userInput.addEventListener('keypress', function handleKeyPress(e) {
                            if (e.key === 'Enter') {
                                const value = userInput.value.trim();
                                userInput.value = '';
                                if (value) {
                                    const [brand, model, type] = value.split(',').map(v => v.trim());
                                    vehicleDetails[currentVehicleIndex] = { brand, model, type };
                                    currentVehicleIndex++;
                                    userInput.removeEventListener('keypress', handleKeyPress);
                                    askForVehicleDetails();
                                }
                                chatBox.scrollTop = chatBox.scrollHeight;
                            }
                        });
                    };

                    const promptForVehicleChoice = () => {
                        const botMessage = document.createElement('div');
                        botMessage.className = 'chat-message bot';
                        botMessage.textContent = "Choose a vehicle for price recommendations (Vehicle 1 or Vehicle 2): & Click the 'Enter' key on your keyboard";
                        chatBox.appendChild(botMessage);
                    
                        userInput.addEventListener('keypress', function handleKeyPress(e) {
                            if (e.key === 'Enter') {
                                const choice = userInput.value.trim();
                                userInput.value = '';
                                if (choice === "Vehicle 1" || choice === "Vehicle 2") {
                                    const selectedVehicle = choice === "Vehicle 1" ? vehicleDetails[0] : vehicleDetails[1];
                                    fetchPriceDetails(selectedVehicle);
                                } else {
                                    appendBotMessage("Invalid choice. Please type 'Vehicle 1' or 'Vehicle 2'.");
                                }
                                userInput.removeEventListener('keypress', handleKeyPress);
                            }
                            chatBox.scrollTop = chatBox.scrollHeight;
                        });
                    };

                    const startPriceRecommendations = () => {
                        const botMessage = document.createElement('div');
                        botMessage.className = 'chat-message bot';
                        botMessage.textContent = "Choose a vehicle for price recommendations (Vehicle 1 or Vehicle 2): and click 'Enter' Key on your keyboard";
                        chatBox.appendChild(botMessage);
                
                        userInput.addEventListener('keypress', function handleKeyPress(e) {
                            if (e.key === 'Enter') {
                                const choice = userInput.value.trim();
                                userInput.value = '';
                                if (choice === "Vehicle 1" || choice === "Vehicle 2") {
                                    const selectedVehicle = choice === "Vehicle 1" ? vehicleDetails[0] : vehicleDetails[1];
                                    fetchPriceDetails(selectedVehicle);
                                } else {
                                    appendBotMessage("Invalid choice. Please type 'Vehicle 1' or 'Vehicle 2'.");
                                }
                                userInput.removeEventListener('keypress', handleKeyPress);
                            }
                            chatBox.scrollTop = chatBox.scrollHeight;
                        });
                    };
                
                    const fetchPriceDetails = (vehicle) => {
                        fetch('/price_recommendations/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken(),
                            },
                            body: JSON.stringify({ vehicle }),
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === "success") {
                                const details = data.price_details;
                                const vehicleDetails = data.vehicle_details;

                                // Add vehicle details to the object
                                const fullVehicleDetails = {
                                    ...vehicleDetails,
                                    price: details.Price,
                                    tax: details.Tax,
                                    total_price: details["Total Price"],
                                    downpayment: details.Downpayment,
                                };
                
                                // Display Final Price and Down Payment
                                const botMessage = document.createElement('div');
                                botMessage.className = 'chat-message bot';
                                botMessage.innerHTML = `
                                    Price Recommendations:<br>
                                    Final Price: LKR ${details["Total Price"]}.00<br>
                                    Downpayment: LKR ${details["Downpayment"]}.00<br>
                                    <br>To confirm, please type 'Yes' and click 'Enter' Key on your keyboard.
                                `;
                                chatBox.appendChild(botMessage);
                                
                                // Prompt for confirmation
                                promptForConfirmation(fullVehicleDetails);
                            } else {
                                appendBotMessage(data.message || 'An error occurred while fetching price recommendations.');
                            }
                            chatBox.scrollTop = chatBox.scrollHeight;
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            appendBotMessage('An error occurred. Please try again later.');
                        });
                    };
                
                    const promptForConfirmation = (vehicleDetails) => {
                        userInput.addEventListener('keypress', function handleKeyPress(e) {
                            if (e.key === 'Enter') {
                                const confirmation = userInput.value.trim().toLowerCase();
                                userInput.value = '';
                                if (confirmation === "yes") {
                                    // Display confirmation message
                                    const botMessage = document.createElement('div');
                                    botMessage.className = 'chat-message bot';
                                    botMessage.innerHTML = `
                                        Congratulations!<br>
                                        You have confirmed to buy the vehicle.<br>
                                        <br>
                                        Agreement Details:<br>
                                        Brand: ${vehicleDetails.brand}<br>
                                        Model: ${vehicleDetails.model}<br>
                                        Type: ${vehicleDetails.type}<br>
                                        Category: ${vehicleDetails.category}<br>
                                        Price: LKR ${vehicleDetails.price}.00<br>
                                        Year: ${vehicleDetails.year}<br>
                                        Fuel Type: ${vehicleDetails.fuel_type}<br>
                                        Mileage: ${vehicleDetails.mileage}<br>
                                        Transmission: ${vehicleDetails.transmission}<br>
                                        Safety Rating: ${vehicleDetails.safety_rating}<br>
                                        Warranty: ${vehicleDetails.warranty}<br>
                                        <br>
                                        Please provide us the installment months that are suitable for you (12, 24, or 36) and click 'Enter' Key on your keyboard.
                                    `;
                                    chatBox.appendChild(botMessage);
                    
                                    // Prompt for installment months
                                    promptForInstallmentMonths(vehicleDetails);
                                } else {
                                    appendBotMessage("Confirmation not received. Please type 'Yes' to confirm.");
                                }
                                userInput.removeEventListener('keypress', handleKeyPress);
                            }
                            chatBox.scrollTop = chatBox.scrollHeight;
                        });
                    };
                    
                    const promptForInstallmentMonths = (vehicleDetails) => {
                        userInput.addEventListener('keypress', function handleKeyPress(e) {
                            if (e.key === 'Enter') {
                                const months = parseInt(userInput.value.trim());
                                userInput.value = '';
                                if ([12, 24, 36].includes(months)) {
                                    fetchInstallmentDetails(vehicleDetails, months);
                                } else {
                                    appendBotMessage("Invalid input. Please type 12, 24, or 36 for installment months.");
                                }
                                userInput.removeEventListener('keypress', handleKeyPress);
                            }
                            chatBox.scrollTop = chatBox.scrollHeight;
                        });
                    };
                    
                    const fetchInstallmentDetails = (vehicleDetails, months) => {
                        fetch('/price_recommendations/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken(),
                            },
                            body: JSON.stringify({ vehicle: vehicleDetails, installment_months: months }),
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === "success") {
                                const details = data.price_details;
                    
                                // Display installment details
                                const botMessage = document.createElement('div');
                                botMessage.className = 'chat-message bot';
                                botMessage.innerHTML = `
                                    Installment Details:<br>
                                    Price: LKR ${details.Price}.00<br>
                                    Tax: LKR ${details.Tax}.00<br>
                                    Total Price: LKR ${details["Total Price"]}.00<br>
                                    Downpayment: LKR ${details.Downpayment}.00<br>
                                    Installment Months: ${details["Installment Months"]}<br>
                                    Monthly Payment: LKR ${details["Monthly Payment"]}.00<br>
                                    <br>Thank you for choosing us!
                                `;
                                chatBox.appendChild(botMessage);
                            } else {
                                appendBotMessage(data.message || 'An error occurred while fetching installment details.');
                            }
                            chatBox.scrollTop = chatBox.scrollHeight;
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            appendBotMessage('An error occurred. Please try again later.');
                        });
                    };
                
                    // Start the workflow
                    askForVehicleDetails();
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
    ['ID', 'Brand', 'Model', 'Category', 'Year', 'Fuel Type', 'Price'].forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Populate table rows with vehicle data
    vehicles.forEach(vehicle => {
        const row = document.createElement('tr');
        ['ID', 'Brand', 'Model', 'Category', 'Year', 'Fuel Type', 'Price'].forEach(key => {
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

let currentStep = "default";
let state = {
    vehicleName: null, 
};

const sendMultiStepMessage = () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (message) {
        // Display user message
        const userMessage = document.createElement('div');
        userMessage.className = 'chat-message user';
        userMessage.textContent = message;
        chatBox.appendChild(userMessage);

        userInput.value = '';

        // Handle "start over" command
        if (message.toLowerCase() === "start over") {
            // Display a bot message indicating the interaction is restarting
            const botMessage = document.createElement('div');
            botMessage.className = 'chat-message bot';
            chatBox.appendChild(botMessage);

            chatBox.scrollTop = chatBox.scrollHeight;

            // Reset the state
            currentStep = "default";
            state.vehicleName = null;

            // Send a request to the backend to reset the interaction flow
            fetch('/multi_step_interaction/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ query: "start over", user_id: 'default_user' }) // Replace 'default_user' with dynamic user ID if needed
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    // Display the response from the backend
                    const restartMessage = document.createElement('div');
                    restartMessage.className = 'chat-message bot';
                    restartMessage.textContent = data.response;
                    chatBox.appendChild(restartMessage);

                    chatBox.scrollTop = chatBox.scrollHeight;
                } else {
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'chat-message bot';
                    errorMessage.textContent = data.message || 'An error occurred while restarting the interaction.';
                    chatBox.appendChild(errorMessage);

                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            })
            .catch(error => {
                console.error('Error:', error);

                const errorMessage = document.createElement('div');
                errorMessage.className = 'chat-message bot';
                errorMessage.textContent = 'An error occurred. Please try again later.';
                chatBox.appendChild(errorMessage);

                chatBox.scrollTop = chatBox.scrollHeight;
            });

            return;
        }


        // Handle "Options" command
        if (message.toLowerCase() === "options") {
            // Trigger the "Let's get started!" button functionality
            const startButton = document.querySelector('.start-button');
            if (startButton && startButton.onclick) {
                startButton.onclick();
            }
            return;
        }

        // Handle "recommend me" command
        if (message.toLowerCase() === "recommend me") {
            // Respond to the "recommend me" command
            const botMessage = document.createElement('div');
            botMessage.className = 'chat-message bot';
            botMessage.textContent = "Ask me questions related to recommendations.";
            chatBox.appendChild(botMessage);

            // Set the current step to "semantic_query"
            currentStep = "semantic_query";

            chatBox.scrollTop = chatBox.scrollHeight;
            return;
        }

        // Add loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading-indicator';
        loadingIndicator.textContent = 'Typing...';
        chatBox.appendChild(loadingIndicator);

        chatBox.scrollTop = chatBox.scrollHeight;

        // Check if the user is in the "Compare Vehicles" step
        if (currentStep === "compare_vehicles") {
            // Send the input to the /compare/ endpoint
            fetch('/compare/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ vehicles: message }),
            })
            .then(response => response.json())
            .then(data => {
                chatBox.removeChild(loadingIndicator);

                if (data.status === "success") {
                    renderComparisonTable(data.comparison);

                    // Display next options (e.g., "📊 View Specifications")
                    if (data.next_options) {
                        displayNextOptions(data.next_options);
                    }
                } else {
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                    botMessage.textContent = data.message;
                    chatBox.appendChild(botMessage);
                }

                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
                chatBox.removeChild(loadingIndicator);

                const botMessage = document.createElement('div');
                botMessage.className = 'chat-message bot';
                botMessage.textContent = 'An error occurred. Please try again later.';
                chatBox.appendChild(botMessage);

                // Scroll to the bottom of the chat box
                chatBox.scrollTop = chatBox.scrollHeight;   
            });
        } else if (currentStep === "view_specifications") {
            // Send the input to the /specifications/ endpoint
            fetch('/specifications/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ vehicle_name: message }),
            })
            .then(response => response.json())
            .then(data => {
                chatBox.removeChild(loadingIndicator);

                if (data.status === "success") {
                    renderSpecifications(data.specifications);

                    // Display next options (e.g., "💰 Financial Options")
                    if (data.next_options) {
                        displayNextOptions(data.next_options);
                    }
                } else {
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                    botMessage.textContent = data.message;
                    chatBox.appendChild(botMessage);
                }

                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
                chatBox.removeChild(loadingIndicator);

                const botMessage = document.createElement('div');
                botMessage.className = 'chat-message bot';
                botMessage.textContent = 'An error occurred. Please try again later.';
                chatBox.appendChild(botMessage);

                // Scroll to the bottom of the chat box
                chatBox.scrollTop = chatBox.scrollHeight;
            });
        } else if (currentStep === "financial_options") {
            // Check if the user has already provided the vehicle name
            if (!state.vehicleName) {
                state.vehicleName = message; // Save the vehicle name
                const botMessage = document.createElement('div');
                botMessage.className = 'chat-message bot';
                botMessage.textContent = "Please provide the installment months (e.g., 12, 24, 36, 48).";
                chatBox.appendChild(botMessage);

                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                // Send the vehicle name and installment months to the backend
                fetch('/financial_options/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken(),
                    },
                    body: JSON.stringify({
                        vehicle_name: state.vehicleName,
                        installment_months: parseInt(message, 10) // Convert the message to an integer
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    chatBox.removeChild(loadingIndicator);

                    if (data.status === "success") {
                        const botMessage = document.createElement('div');
                        botMessage.className = 'chat-message bot';
                        botMessage.textContent = "Here are the finance details for the selected vehicle:";
                        chatBox.appendChild(botMessage);

                        renderSpecifications(data.finance_details); 

                        // Display next options (e.g., "💰 Financial Options")
                        if (data.next_options) {
                            displayNextOptions(data.next_options);
                        }
                    } else {
                        const botMessage = document.createElement('div');
                        botMessage.className = 'chat-message bot';
                        botMessage.textContent = data.message;
                        chatBox.appendChild(botMessage);
                    }

                    chatBox.scrollTop = chatBox.scrollHeight;
                })
                .catch(error => {
                    console.error('Error:', error);
                    chatBox.removeChild(loadingIndicator);

                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                    botMessage.textContent = 'An error occurred. Please try again later.';
                    chatBox.appendChild(botMessage);
                });

                // Reset the state after sending the request
                state.vehicleName = null;
            }
        } else if (currentStep === "choose_vehicle") {
            fetch('/choose_vehicle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ vehicle_name: message })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response from /choose_vehicle/:", data); // Debugging log
        
                chatBox.removeChild(loadingIndicator);
        
                if (data.status === "success") {
                    state.vehicleName = message;
                    
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                
                    // Use innerHTML to format the response with line breaks and emojis
                    botMessage.innerHTML = `
                        🎯 <strong>You’ve selected:</strong> <span style="color: #007BFF;">Honda City Sedan</span><br>
                        📞 <strong>Seller Info:</strong><br>
                        • <strong>Dealer:</strong> SriLankaCars<br>
                        • <strong>Phone:</strong> <a href="tel:94760364691" style="color: #007BFF; text-decoration: none;">94760364691</a><br>
                        • <strong>Email:</strong> <a href="mailto:srilankacars@gmail.com" style="color: #007BFF; text-decoration: none;">srilankacars@gmail.com</a><br>
                        • <strong>Location:</strong> Kandy<br>
                        <hr style="border: 1px solid #ccc; margin: 10px 0;">
                        ❓ <strong>Would you recommend this vehicle to others?</strong><br>
                        <p class="option" style="margin: 5px;">👍 Yes</p>
                        <p class="option" style="margin: 5px;">👎 No</p>
                    `;
                
                    chatBox.appendChild(botMessage);
                    chatBox.scrollTop = chatBox.scrollHeight;
        
                    // Display recommendation options (👍 Yes, 👎 No)
                    displayNextOptions(["👍 Yes", "👎 No"]);
                } else {
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                    botMessage.textContent = data.message || 'Sorry, I could not process your request.';
                    chatBox.appendChild(botMessage);
                }
        
                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
                chatBox.removeChild(loadingIndicator);
        
                const botMessage = document.createElement('div');
                botMessage.className = 'chat-message bot';
                botMessage.textContent = 'An error occurred. Please try again later.';
                chatBox.appendChild(botMessage);
            });
        } else if (currentStep === "semantic_query") {
            // Handle semantic queries
            fetch('/semantic_query/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ query: message })
            })
            .then(response => response.json())
            .then(data => {
                // Safely remove the loading indicator if it exists
                if (loadingIndicator && loadingIndicator.parentNode) {
                    chatBox.removeChild(loadingIndicator);
                }

                if (data.status === "success" && data.data && data.data.length > 0) {
                    // Display the bot's response
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                    botMessage.textContent = data.response;
                    chatBox.appendChild(botMessage);

                    // Render the database table with the results
                    renderDatabaseTable(data.data);
                } else {
                    // Display a user-friendly message if no vehicles are found
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                    botMessage.textContent = data.message || 'Sorry, no vehicles were found matching your query.';
                    chatBox.appendChild(botMessage);
                }

                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);

                // Safely remove the loading indicator if it exists
                if (loadingIndicator && loadingIndicator.parentNode) {
                    chatBox.removeChild(loadingIndicator);
                }

                const botMessage = document.createElement('div');
                botMessage.className = 'chat-message bot';
                botMessage.textContent = 'An error occurred. Please try again later.';
                chatBox.appendChild(botMessage);

                chatBox.scrollTop = chatBox.scrollHeight;
            });
        } else {
            // Send the message to the multi-step interaction endpoint
            fetch('/multi_step_interaction/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ query: message, user_id: 'default_user' }) // Replace 'default_user' with dynamic user ID if needed
            })
            .then(response => response.json())
            .then(data => {
                chatBox.removeChild(loadingIndicator);

                if (data.status === "success") {
                    // Display bot response
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                    botMessage.textContent = data.response;
                    chatBox.appendChild(botMessage);

                    // If vehicles are included in the response, render them
                    if (data.vehicles && Array.isArray(data.vehicles)) {
                        renderVehicleData(data.vehicles);
                    }

                    // If next_options are included in the response, display them
                    if (data.next_options) {
                        displayNextOptions(data.next_options);
                    }
                } else {
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message bot';
                    botMessage.textContent = data.message || 'Sorry, I could not process your request.';
                    chatBox.appendChild(botMessage);
                }

                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
                chatBox.removeChild(loadingIndicator);

                const botMessage = document.createElement('div');
                botMessage.className = 'chat-message bot';
                botMessage.textContent = 'An error occurred. Please try again later.';
                chatBox.appendChild(botMessage);

                // Scroll to the bottom of the chat box
                chatBox.scrollTop = chatBox.scrollHeight;
            });

            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }
};


const renderVehicleData = (vehicles) => {
    const chatBox = document.getElementById('chat-box');

    const table = document.createElement('table');
    table.className = 'vehicle-table';

    // Create table header
    const headerRow = document.createElement('tr');
    ['Vehicle', 'Price', 'Year', 'Fuel Type', 'Mileage', 'Transmission'].forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Populate table rows with vehicle data
    vehicles.forEach(vehicle => {
        const row = document.createElement('tr');
        ['Vehicle', 'Price', 'Year', 'Fuel Type', 'Mileage', 'Transmission'].forEach(key => {
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


function displayNextOptions(options) {
    const chatBox = document.getElementById('chat-box');

    // Create a container for the options
    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'options-container';

    // Create a button for each option
    options.forEach(option => {
        const optionButton = document.createElement('button');
        optionButton.className = 'option-button';
        optionButton.textContent = option;

        // Add click event listener for each button
        optionButton.onclick = () => {
            // Simulate user selecting an option
            const userMessage = document.createElement('div');
            userMessage.className = 'chat-message user';
            userMessage.textContent = option;
            chatBox.appendChild(userMessage);

            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;

            // Handle the selected option
            handleOptionSelection(option);
        };

        optionsContainer.appendChild(optionButton);
    });

    // Append the options container to the chat box
    chatBox.appendChild(optionsContainer);

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;
}



function handleOptionSelection(option) {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');

    if (option === "🔍 Compare Vehicles") {
        currentStep = "compare_vehicles"; // Update the current step

        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message bot';
        botMessage.textContent = "Please specify the two vehicles you'd like to compare (e.g., 'Toyota Camry SUV Van and Toyota Yaris SUV SUV').";
        chatBox.appendChild(botMessage);

        chatBox.scrollTop = chatBox.scrollHeight;
    } else if (option === "📊 View Specifications") {
        currentStep = "view_specifications"; // Update the current step

        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message bot';
        botMessage.textContent = "Please provide the vehicle name (e.g., 'Toyota Camry SUV Van').";
        chatBox.scrollTop = chatBox.scrollHeight;
        chatBox.appendChild(botMessage);

        chatBox.scrollTop = chatBox.scrollHeight;
    } else if (option === "💰 Financial Options") {
        currentStep = "financial_options"; // Update the current step

        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message bot';
        botMessage.textContent = "Please provide the vehicle name (e.g., 'Toyota Camry SUV Van').";
        chatBox.scrollTop = chatBox.scrollHeight;
        chatBox.appendChild(botMessage);

        chatBox.scrollTop = chatBox.scrollHeight;
    } else if (option === "✅ Choose a Vehicle") { 
        currentStep = "choose_vehicle"; // Update the current step

        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message bot';
        botMessage.textContent = "Please provide the vehicle name (e.g., 'Toyota Camry SUV Van').";
        chatBox.scrollTop = chatBox.scrollHeight;
        chatBox.appendChild(botMessage);

        chatBox.scrollTop = chatBox.scrollHeight;
    } else if (option === "👍 Yes") {
        // Handle "Yes" response
        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message bot';
        botMessage.innerHTML = `
            🎉 Thank you for your feedback! I'm glad I could help.<br>
            Also I can provide you most recommended vehicle details. just type "recommend me"<br>
            If you’d like to search again, just type "start over" anytime.<br>
            Have a smooth ride ahead! 🚗✨
        `;
        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    
        // Send the recommendation to the backend
        if (state.vehicleName) {
            fetch('/update_recommendation/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ vehicle_name: state.vehicleName }) // Send the vehicle name
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    console.log("Recommendation updated successfully.");
                } else {
                    console.error("Failed to update recommendation:", data.message);
                }
            })
            .catch(error => {
                console.error("Error updating recommendation:", error);
            });
        } else {
            console.error("Vehicle name is not set in the state.");
        }
    } else if (option === "👎 No") {
        // Handle "No" response
        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message bot';
        botMessage.innerHTML = `
        "I'm sorry to hear that.<br> 
        I can provide you most recommended vehicle details. just type \"recommend me\".<br> 
        Let me know how I can assist you further.<br> If you’d like to search again, just type \"start over\" anytime.<br> 
        Have a smooth ride ahead! 🚗✨"`;
        
        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    } 
}



function renderDatabaseTable(data) {
    const chatBox = document.getElementById('chat-box');

    const table = document.createElement('table');
    table.className = 'database-table';

    // Define the important columns to display
    const importantColumns = ['Brand', 'Model', 'Price', 'Year', 'Mileage'];

    // Create table header
    const headerRow = document.createElement('tr');
    importantColumns.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Populate table rows with data
    data.forEach(row => {
        const dataRow = document.createElement('tr');
        importantColumns.forEach(key => {
            const td = document.createElement('td');
            td.textContent = row[key.toLowerCase()] || 'N/A'; 
            dataRow.appendChild(td);
        });
        table.appendChild(dataRow);
    });

    // Append the table to the chat box
    const botResponse = document.createElement('div');
    botResponse.className = 'chat-message bot';
    botResponse.appendChild(table);
    chatBox.appendChild(botResponse);

    chatBox.scrollTop = chatBox.scrollHeight;
}



function renderComparisonTable(comparison) {
    const chatBox = document.getElementById('chat-box');
    const table = document.createElement('table');
    table.className = 'comparison-table';

    // Create table header
    const headerRow = document.createElement('tr');
    ['Feature', 'Vehicle 1', 'Vehicle 2'].forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Populate table rows with comparison data
    comparison.Feature.forEach((feature, index) => {
        const row = document.createElement('tr');

        const featureCell = document.createElement('td');
        featureCell.textContent = feature;
        row.appendChild(featureCell);

        const vehicle1Cell = document.createElement('td');
        vehicle1Cell.textContent = comparison[Object.keys(comparison)[1]][index];
        row.appendChild(vehicle1Cell);

        const vehicle2Cell = document.createElement('td');
        vehicle2Cell.textContent = comparison[Object.keys(comparison)[2]][index];
        row.appendChild(vehicle2Cell);

        table.appendChild(row);
    });

    // Append the table to the chat box
    const botResponse = document.createElement('div');
    botResponse.className = 'chat-message bot';
    botResponse.appendChild(table);
    chatBox.appendChild(botResponse);

    chatBox.scrollTop = chatBox.scrollHeight;
}


function renderSpecifications(specifications) {
    const chatBox = document.getElementById('chat-box');
    const table = document.createElement('table');
    table.className = 'specifications-table';

    // Populate table rows with specifications
    for (const [key, value] of Object.entries(specifications)) {
        const row = document.createElement('tr');

        const keyCell = document.createElement('td');
        keyCell.textContent = key;
        row.appendChild(keyCell);

        const valueCell = document.createElement('td');
        valueCell.textContent = value;
        row.appendChild(valueCell);

        table.appendChild(row);
    }

    // Append the table to the chat box
    const botResponse = document.createElement('div');
    botResponse.className = 'chat-message bot';
    botResponse.appendChild(table);
    chatBox.appendChild(botResponse);

    chatBox.scrollTop = chatBox.scrollHeight;
}