document.addEventListener('DOMContentLoaded', function() {
    const numDestinationsInput = document.getElementById('numDestinations');
    const destinationsContainer = document.getElementById('destinationsContainer');
    const travelingMethodSelect = document.getElementById('travelingMethod');
    const profileIcon = document.getElementById('profileIcon');
    const profilePopup = document.getElementById('profilePopup');

    // Create destination fields based on the number of destinations
    function createDestinationFields(num) {
        destinationsContainer.innerHTML = ''; // Clear the container before adding new inputs
        for (let i = 0; i < num; i++) { // Start index from 0 for Flask's FieldList
            const destination = document.createElement('div');
            destination.classList.add('destination');
            destination.innerHTML = `
                <div class="input-line">
                    <div class="form-group">
                        <label for="destination${i}">Destination ${i + 1}:</label>
                        <input type="text" id="destination${i}" name="destinations-${i}-destination" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="hotel${i}">Preferred Hotel Name:</label>
                        <input type="text" id="hotel${i}" name="destinations-${i}-hotel" class="form-control" required>
                    </div>
                    <div class="form-group travel-preference" style="display:none;">
                        <label for="travelPreference${i}">Travel Preference:</label>
                        <select id="travelPreference${i}" name="destinations-${i}-travel_preference" class="form-control">
                            <option value="">Select travel preference</option>
                            <option value="air">Air</option>
                            <option value="train">Train</option>
                            <option value="bus">Bus</option>
                            <option value="car">Car</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="NumberOfDays${i}">Number of Stay Days:</label>
                        <input type="number" id="NumberOfDays${i}" name="destinations-${i}-number_of_days" class="form-control" required>
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
    createDestinationFields(numDestinationsInput.value);

    // Profile popup functionality
    profileIcon.addEventListener('click', function(e) {
        e.stopPropagation();
        profilePopup.style.display = profilePopup.style.display === 'block' ? 'none' : 'block';
    });

    document.addEventListener('click', function(e) {
        if (!profilePopup.contains(e.target) && e.target !== profileIcon) {
            profilePopup.style.display = 'none';
        }
    });

    // Close the popup on page load
    profilePopup.style.display = 'none';
});
