prompt = """
You are tasked with generating a personalized travel itinerary based on the following user preferences. The goal is to create a comprehensive, day-by-day plan that includes real-time weather conditions, accurately calculates the total budget and spending amounts, and incorporates special occasions like festivals, parties, and local events. The itinerary should consider the user’s selected theme, and travel preferences for each destination, and ensure that all activities, transportation, accommodations, and meals fit within the specified budget.

Please ensure that the following aspects are thoroughly covered in the itinerary:

Destination Details: Include a brief introduction to each destination, highlighting its significance, famous attractions, and why it's worth visiting.

Real-Time Weather Information: Provide detailed weather updates for each part of the day:

Morning (8:00 AM - 12:00 PM): Mention temperature, rain chance, wind speed, and safety tips (e.g., sunscreen, jackets).
Afternoon (12:00 PM - 6:00 PM): Offer relevant weather insights, particularly if the user will be outdoors, and suggest any additional clothing items needed.
Evening (6:00 PM - 9:00 PM): Highlight temperature drops or evening conditions, and safety tips (e.g., light jackets, umbrellas).
Transportation and Travel Preferences: Use the travel preference selected by the user for each destination (e.g., bus, train, air, car, mix). For mixed preferences, provide the best possible route and mode of travel for each segment of the journey. Be sure to explain connections and any transfers required.

Budget Breakdown: For each activity, meal, and accommodation, provide a cost estimate and ensure that the total budget stays within the amount provided by the user. If applicable, break down the cost per person and outline any expected surcharges or taxes.

Accommodations: Suggest hotels, hostels, or guesthouses based on the user’s preference and selected budget. Include details about amenities and proximity to key attractions.

Daily Activities and Sightseeing: Suggest a well-balanced itinerary that includes adventure, relaxation, cultural immersion, and must-see tourist attractions, aligning with the predefined theme (e.g., adventure, relaxation, honeymoon, family vacation). Include morning, afternoon, and evening activities with suggested times.

Meals: Recommend meals and dining experiences based on the user’s food preferences. Include local dining options, street food, and traditional cuisine wherever possible.

Special Events and Occasions: Incorporate any local festivals, special events, or parties that coincide with the travel dates. Provide details about timings, entry fees, and the cultural significance of these events.

Group Size: Tailor the itinerary according to the group size and ensure that any group-specific discounts or arrangements are noted.

Travel Tips and Safety: Provide essential travel tips, such as safety precautions, advice on local customs, and any specific considerations for each destination. Mention things like dress codes for religious sites, keeping personal belongings safe, and how to interact with the locals respectfully.

Souvenirs and Shopping: Allocate time and budget for shopping for souvenirs or local crafts at markets or boutiques.

Departure and Final Reflection: Conclude the trip with a summary of the final day's activities, including checkout from accommodations, final sightseeing, and travel details for returning to the user’s origin city. Include transportation options back and suggest an appropriate time to depart to avoid traffic or delays.

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

Sample Itinerary Output
Day 1: {startDate} - Arrival & {predefinedTheme} Exploration
Morning (8:00 AM - 12:00 PM):

Weather Report: Expect {weather_morning}. Suggest necessary precautions like {precautions_morning}.
Activity: Depart from {fromLocation} (based on the preferred mode of transport - {travelingMethod}). Arrive in {destination_1} by {arrival_time}.
Accommodation: Check into your selected accommodation based on your {totalBudget}.
Afternoon (12:00 PM - 6:00 PM):

Weather Report: The afternoon will be {weather_afternoon}. Suggestions: {precautions_afternoon}.
Activity: Explore {key_attractions}. Based on your theme, you may want to {theme_activity_afternoon}.
Lunch: Enjoy {recommended_lunch_spot}.
Evening (6:00 PM - 9:00 PM):

Weather Report: Evening conditions are expected to be {weather_evening}. Recommendations include {precautions_evening}.
Activity: {evening_activity}.
Dinner: Savor {dinner_recommendation}.
Total Estimated Cost for Day 1:

- Transportation: ₹{transport_cost}
- Lunch: ₹{lunch_cost}
- Dinner: ₹{dinner_cost}
- Accommodation: ₹{accommodation_cost}

Day 2: {next_day} - Cultural & Sightseeing
Morning (8:00 AM - 12:00 PM):

Weather Report: Expect {weather_morning_day2}.
Activity: Visit {morning_activity}. 
Breakfast: Enjoy {breakfast_suggestion}.
"""