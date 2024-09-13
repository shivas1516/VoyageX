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

Sample Itinerary Output
Day 1: 15th September 2025 (Monday) - Arrival & Adventure
Morning (8:00 AM - 12:00 PM):

Weather Report: Expect partly cloudy skies with temperatures around 28°C (82°F). There’s a slight chance of rain (20%), so carrying a light raincoat or umbrella is advisable. Winds will be mild at 10 km/h from the southeast. Wear light, breathable clothing and comfortable walking shoes.
Activity: Depart from Chennai (based on the preferred mode of transport - bus or train). Arrive in Thiruvannamalai by noon (approximately 3-4 hours journey).
Accommodation: Check into your chosen budget-friendly accommodation (suggestions include local hostels or guesthouses).
Afternoon (12:00 PM - 6:00 PM):

Weather Report: The afternoon will be hot, with temperatures rising to 32°C (90°F). Keep hydrated, wear a hat or sunglasses, and apply sunscreen frequently.
Activity: Explore Annamalaiyar Temple or go for an adventurous hike up Arunachala Hill. For hikers, the 2-hour trek will offer stunning views of the town and surrounding landscape. Those preferring a slower pace can visit the temple for spiritual exploration.
Lunch: Enjoy a traditional South Indian meal at a local restaurant.
Evening (6:00 PM - 9:00 PM):

Weather Report: Temperatures will cool to around 25°C (77°F) in the evening. Light breezes and pleasant conditions are expected, but carry a light jacket in case it gets chilly.
Activity: Attend the evening aarti (prayer ceremony) at the Annamalaiyar Temple.
Dinner: Savor a South Indian dinner at a local restaurant or enjoy some street food.
Total Estimated Cost for Day 1:

Transportation: ₹500 (train/bus ticket per person)
Lunch: ₹300 per person
Dinner: ₹350 per person
Accommodation: ₹1,000 per night (budget option)
Day 2: 16th September 2025 (Tuesday) - Cultural Exploration
Morning (8:00 AM - 12:00 PM):

Weather Report: Clear skies with temperatures around 27°C (81°F). Perfect for a morning exploration.
Activity: After breakfast, visit Ramanashram for a cultural immersion into the teachings of the renowned sage Ramana Maharshi.
Breakfast: Enjoy a local breakfast at a nearby street vendor (suggestions include dosa, idli, or vada with coconut chutney).
Afternoon (12:00 PM - 6:00 PM):

Weather Report: The afternoon will be warm, with temperatures peaking at 33°C (91°F). Carry water, wear sunglasses, and protect yourself from the sun.
Activity: Visit Virupaksha Cave and Skanda Ashram, two historical and spiritual locations with rich significance.
Lunch: A relaxed meal at a local restaurant, trying more regional specialties.
Evening (6:00 PM - 9:00 PM):

Weather Report: The evening will be cooler, around 24°C (75°F). A pleasant time to wind down the day.
Activity: Take a stroll around the town square or visit a temple tank to reflect and relax.
Dinner: Dinner at a restaurant known for authentic South Indian cuisine.
Total Estimated Cost for Day 2:

Breakfast: ₹150 per person
Lunch: ₹350 per person
Dinner: ₹400 per person
Entrance fees: ₹100 (combined for both sites)
Day 3: 17th September 2025 (Wednesday) - Departure & Memories
Morning (8:00 AM - 10:00 AM):

Weather Report: Sunny with mild temperatures around 26°C (79°F). Perfect for a final morning in town.
Activity: After breakfast, enjoy some last-minute souvenir shopping or explore the local markets for crafts.
Breakfast: A light breakfast at the hotel.
Afternoon (10:00 AM - 12:00 PM):

Activity: Depart Thiruvannamalai for Chennai. Travel options include bus or train, based on your preferences.
Final Tip: Reflect on your trip and the memorable experiences you’ve had.
Total Estimated Cost for Day 3:

Breakfast: ₹150 per person
Transportation: ₹500 per person
Budget Summary:

Total Transportation: ₹1,500 per person
Total Meals: ₹1,400 per person
Total Accommodation: ₹2,000 per person
Activities and Miscellaneous: ₹300 per person
Grand Total per Person: ₹5,200
"""