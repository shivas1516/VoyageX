document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('travelForm');
    const numDestinationsInput = document.getElementById('numDestinations');
    const destinationsContainer = document.getElementById('destinationsContainer');
    const travelingMethodSelect = document.getElementById('travelingMethod');
    const responseContainer = document.getElementById('responseContainer');
    const responseContent = document.getElementById('responseContent');
    const downloadPdfButton = document.getElementById('downloadPdf');

    function createDestinationFields(num) {
        destinationsContainer.innerHTML = '';
        for (let i = 1; i <= num; i++) {
            const destination = document.createElement('div');
            destination.classList.add('destination');
            destination.innerHTML = `
                <div class="input-line">
                    <div class="form-group">
                        <label for="destination${i}">Destination ${i}:</label>
                        <input type="text" id="destination${i}" name="destination${i}" required>
                    </div>
                    <div class="form-group">
                        <label for="hotel${i}">Preferred Hotel Name:</label>
                        <input type="text" id="hotel${i}" name="hotel${i}" required>
                    </div>
                    <div class="form-group travel-preference" style="display:none;">
                        <label for="travelPreference${i}">Travel Preference:</label>
                        <select id="travelPreference${i}" name="travelPreference${i}">
                            <option value="">Select travel preference</option>
                            <option value="air">Air</option>
                            <option value="train">Train</option>
                            <option value="bus">Bus</option>
                            <option value="car">Car</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="Number of Days${i}">Number Stay Days:</label>
                        <input type="number" textarea id="Number od Days${i}" name="Number od Days${i}" rows="1"></textarea>
                    </div>
                </div>
            `;
            destinationsContainer.appendChild(destination);
        }
        updateTravelPreferences();
    }

    function updateTravelPreferences() {
        const isMix = travelingMethodSelect.value === 'mix';
        document.querySelectorAll('.travel-preference').forEach(el => {
            el.style.display = isMix ? 'block' : 'none';
        });
    }
    
    numDestinationsInput.addEventListener('change', function() {
        createDestinationFields(this.value);
    });
    
    travelingMethodSelect.addEventListener('change', updateTravelPreferences);
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const jsonData = {};
        
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });
    
        // Show loading indicator
        const loadingIndicator = document.getElementById('loading-indicator');
        loadingIndicator.style.display = 'block';
    
        // Send POST request to /generate_plan
        fetch('/generate_plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData),
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            // Display the response in a table format
            displayResponse(data);
        })
        .catch(error => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            // Display error message
            console.error('Error:', error);
            displayResponse({ error: 'An error occurred while generating the itinerary. Please try again.' });
        });
    });
    
    function displayResponse(responseData) {
        const responseContainer = document.getElementById('response-container');
        if (responseData.itinerary) {
            // Generate a table to display the itinerary
            const tableHtml = generateTableFromItinerary(responseData.itinerary);
            responseContainer.innerHTML = `<h2>Your Travel Itinerary:</h2>${tableHtml}`;
        } else if (responseData.error) {
            responseContainer.innerHTML = `<h2>Error:</h2><p>${responseData.error}</p>`;
        }
        responseContainer.style.display = 'block';
    }
    
    // Helper function to generate HTML table from the itinerary data
    function generateTableFromItinerary(itinerary) {
        let tableHtml = `
        <table border="1" cellpadding="10" cellspacing="0">
            <thead>
                <tr>
                    <th>Day</th>
                    <th>Time Slot</th>
                    <th>Activity</th>
                    <th>Weather</th>
                    <th>Cost (Estimated)</th>
                </tr>
            </thead>
            <tbody>`;
    
        itinerary.days.forEach(day => {
            day.activities.forEach(activity => {
                tableHtml += `
                <tr>
                    <td>${day.date}</td>
                    <td>${activity.timeSlot}</td>
                    <td>${activity.description}</td>
                    <td>${activity.weather}</td>
                    <td>${activity.cost}</td>
                </tr>`;
            });
        });
    
        tableHtml += `</tbody></table>`;
        return tableHtml;
    }
    

    downloadPdfButton.addEventListener('click', function() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        doc.text("Travel Plan", 10, 10);
        doc.text(responseContent.innerText, 10, 20);
        
        doc.save("travel-plan.pdf");
    });

    // Initialize the form
    createDestinationFields(numDestinationsInput.value);

    // Profile popup functionality
    const profileIcon = document.getElementById('profileIcon');
    const profilePopup = document.getElementById('profilePopup');
    const logoutBtn = document.getElementById('logoutBtn');

    profileIcon.addEventListener('click', function(e) {
        e.stopPropagation();
        profilePopup.style.display = profilePopup.style.display === 'block' ? 'none' : 'block';
    });

    document.addEventListener('click', function(e) {
        if (!profilePopup.contains(e.target) && e.target !== profileIcon) {
            profilePopup.style.display = 'none';
        }
    });

    logoutBtn.addEventListener('click', function() {
        alert('Logout functionality would be implemented here.');
        profilePopup.style.display = 'none';
    });

});