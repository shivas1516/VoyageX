prompt = """
You are tasked with generating a personalized travel itinerary based on the following user preferences. The goal is to create a comprehensive, day-by-day plan that fits within the specified budget and incorporates the user’s selected theme, destinations, and travel preferences. The itinerary should also account for accommodation, meals, and transportation within the given budget.

Please ensure that the following aspects are thoroughly covered in the itinerary:

Destination Details: Include a brief introduction to each destination, highlighting its significance, famous attractions, and why it's worth visiting.

Transportation and Travel Preferences: Use the user’s selected travel method for each destination (e.g., bus, train, air, car, or a mix). For mixed preferences, suggest the best route and mode of travel for each segment of the journey. Explain connections or transfers required, if any.

Budget Breakdown: For each activity, meal, and accommodation, provide a cost estimate and ensure that the total budget stays within the amount provided by the user. If applicable, break down the cost per person and note any surcharges or taxes.

Accommodations: Suggest hotels, hostels, or guesthouses based on the user’s preference and budget. Include details about proximity to key attractions.

Daily Activities and Sightseeing: Suggest a balanced itinerary that includes adventure, relaxation, cultural immersion, and tourist attractions in line with the selected theme (e.g., adventure, relaxation, honeymoon, family vacation). Include morning, afternoon, and evening activities with approximate times.

Meals: Recommend meals and dining options within the user’s budget. Include local dining spots and traditional cuisine wherever possible.

Group Size: Tailor the itinerary according to the group size and note any group discounts or arrangements.

Travel Tips and Safety: Provide general travel tips, such as safety precautions, advice on local customs, and any specific considerations for each destination.

Departure and Final Reflection: Conclude the trip with a summary of the final day's activities, including checkout from accommodations, final sightseeing, and travel details for returning to the user’s origin city. Suggest appropriate times for departure to avoid delays.

User Input:
- From Location: {fromLocation}
- Start Date: {startDate}
- End Date: {endDate}
- Predefined Theme: {predefinedTheme}
- Starting Time: {startTime}
- Returning Time: {returnTime}
- Group Size: {groupSize}
- Total Budget: {totalBudget}
- Number of Destinations: {numDestinations}
- Traveling Method: {travelingMethod}
- Destinations: {destinations}

Sample Itinerary Output:
Day 1: {startDate} - Arrival & {predefinedTheme} Exploration

Morning (8:00 AM - 12:00 PM):
Activity: Depart from {fromLocation} using {travelingMethod}. Arrive in {destinations[0]} by arrival_time.
Accommodation: Check into a hotel or guesthouse within your budget.
Afternoon (12:00 PM - 6:00 PM):
Activity: Explore local attractions in {destinations[0]}. Depending on your theme, enjoy activities such as theme_activity_afternoon.
Lunch: Try local cuisine at a restaurant or food market.
Evening (6:00 PM - 9:00 PM):
Activity: Relax or participate in evening_activity.
Dinner: Enjoy a meal at a recommended dining spot.
Total Estimated Cost for Day 1:
- Transportation: ₹transport_cost
- Lunch: ₹lunch_cost
- Dinner: ₹dinner_cost
- Accommodation: ₹accommodation_cost

Day 2: next_day - Cultural & Sightseeing in {destinations[1]}
Morning (8:00 AM - 12:00 PM):
Activity: Visit cultural landmarks in {destinations[1]}.
Breakfast: Enjoy a local breakfast suggestion.
"""
