document.addEventListener('DOMContentLoaded', function() {
    const responseContainer = document.getElementById('responseContainer');
    const responseContent = document.getElementById('responseContent');
    const downloadPdfButton = document.getElementById('downloadPdf');
    const loadingIndicator = document.getElementById('loading-indicator');

    // Function to display the travel plan
    function displayTravelPlan(planText) {
        responseContent.innerText = planText;
        responseContainer.style.display = 'block'; // Show response container
        downloadPdfButton.style.display = 'block'; // Show download button
    }

    // Function to show the loading indicator
    function showLoadingIndicator() {
        loadingIndicator.style.display = 'block';
    }

    // Function to hide the loading indicator
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

    // Example function to simulate loading and displaying plan (replace with actual usage)
    async function simulateTravelPlan() {
        showLoadingIndicator();

        // Simulate fetching travel plan (replace this with actual data retrieval)
        setTimeout(() => {
            hideLoadingIndicator();
            displayTravelPlan("Your travel plan details go here."); // Replace with actual response
        }, 2000); // Simulated delay
    }

    // Call this function when you want to simulate getting a travel plan
    // simulateTravelPlan();
});
