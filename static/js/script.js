document.addEventListener('DOMContentLoaded', function() {
    const numDestinationsInput = document.getElementById('numDestinations');
    const destinationsContainer = document.getElementById('destinationsContainer');
    const travelingMethodSelect = document.getElementById('travelingMethod');
    const responseContainer = document.getElementById('responseContainer');
    const responseContent = document.getElementById('responseContent');
    const downloadPdfButton = document.getElementById('downloadPdf');
    const loadingIndicator = document.getElementById('loading-indicator');
    const travelForm = document.getElementById('travelForm');

    // Create destination fields based on the number of destinations
    function createDestinationFields(num) {
        destinationsContainer.innerHTML = '';
        for (let i = 1; i <= num; i++) {
            const destination = document.createElement('div');
            destination.classList.add('destination');
            destination.innerHTML = `
                <div class="input-line">
                    <div class="form-group">
                        <label for="destination${i}">Destination ${i}:</label>
                        <input type="text" id="destination${i}" name="destination${i}" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="hotel${i}">Preferred Hotel Name:</label>
                        <input type="text" id="hotel${i}" name="hotel${i}" class="form-control" required>
                    </div>
                    <div class="form-group travel-preference" style="display:none;">
                        <label for="travelPreference${i}">Travel Preference:</label>
                        <select id="travelPreference${i}" name="travelPreference${i}" class="form-control">
                            <option value="">Select travel preference</option>
                            <option value="air">Air</option>
                            <option value="train">Train</option>
                            <option value="bus">Bus</option>
                            <option value="car">Car</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="NumberOfDays${i}">Number of Stay Days:</label>
                        <input type="number" id="NumberOfDays${i}" name="NumberOfDays${i}" class="form-control" required>
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
            el.querySelector('select').required = isMix; // Require if mix is selected
        });
    }

    numDestinationsInput.addEventListener('change', function() {
        createDestinationFields(this.value);
    });

    travelingMethodSelect.addEventListener('change', updateTravelPreferences);

    // Handle form submission
    travelForm.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent default form submission
        showLoadingIndicator(); // Show loading indicator

        const formData = new FormData(travelForm);
        
        try {
            const response = await fetch('/dashboard', { // Update URL if needed
                method: 'POST',
                body: formData,
            });

            hideLoadingIndicator(); // Hide loading indicator

            if (response.ok) {
                const jsonResponse = await response.json();
                if (jsonResponse.success) {
                    displayTravelPlan(jsonResponse.plan.raw_text);
                } else {
                    responseContent.innerText = jsonResponse.message || 'An error occurred.';
                }
            } else {
                responseContent.innerText = 'An error occurred. Please try again.';
            }
        } catch (error) {
            hideLoadingIndicator(); // Hide loading indicator
            console.error('Error:', error);
            responseContent.innerText = 'An unexpected error occurred. Please try again.';
        }
    });

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

    function displayTravelPlan(planText) {
        responseContent.innerText = planText;
        responseContainer.style.display = 'block'; // Show response container
        downloadPdfButton.style.display = 'block'; // Show download button
    }

    function showLoadingIndicator() {
        loadingIndicator.style.display = 'block';
    }

    function hideLoadingIndicator() {
        loadingIndicator.style.display = 'none';
    }

    // PDF download functionality
    downloadPdfButton.addEventListener('click', function() {
        const planText = responseContent.innerText;
        const blob = new Blob([planText], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'travel_plan.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
});
