> **Notice**: I use [Render's free tier](https://docs.render.com/free#other-limitations) to deploy this web application. As a result, the initial loading may take up to 2-3 minutes for the web server to start.

# AI Travel Planner (Itinerary Generator)

This project is an AI-powered travel itinerary generator developed as part of the Altan Fellowship Program tasks. The tool creates a personalized travel plan for users based on their specific preferences, including destinations, travel dates, budget, activities, transportation, and food choices. This planner automates travel itinerary creation with real-time weather conditions, budget breakdowns, and suggestions for accommodations, meals, activities, and transportation.

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Sample Usage](#sample-usage)


## Features

- **Personalized Itinerary**: Tailors travel plans based on user preferences like theme (e.g., adventure, relaxation, family vacation), budget, group size, and selected transportation modes.
- **Real-time Weather Updates**: Provides weather forecasts for morning, afternoon, and evening segments of the day, with appropriate suggestions on clothing and safety tips.
- **Budget Breakdown**: Estimates the costs for activities, meals, accommodation, and transportation to ensure the itinerary fits within the user's budget.
- **Dynamic Accommodation Suggestions**: Recommends hotels, hostels, or guesthouses based on the user’s preference and budget, including details on amenities and proximity to attractions.
- **Day-by-Day Activity Planning**: Suggest a balanced itinerary that includes adventure, cultural immersion, sightseeing, and local experiences aligned with the selected travel theme.
- **Meal Recommendations**: Offers dining suggestions for each meal, incorporating local cuisine and food preferences.
- **Special Events and Local Festivals**: Incorporates local events, festivals, and parties during travel dates.
- **Group Size Customization**: Adjusts the itinerary based on the number of travelers, offering group-specific discounts and arrangements.
- **Travel Tips and Safety**: Provides essential travel tips, including advice on local customs, safety, and cultural etiquette.
- **Shopping and Souvenirs**: Allocates time for shopping and suggests local crafts or souvenirs.
- **Departure Planning**: Concludes with travel tips for returning to the origin city, including transportation options and suggested times to avoid traffic.

## How It Works

The AI Travel Planner is designed to take user inputs through a set of predefined fields such as destination, start and end dates, group size, travel preferences, and budget. Using these inputs, the planner generates a complete, day-by-day itinerary that aligns with the user’s preferences. It calculates the total budget, offers real-time weather forecasts, and recommends activities, accommodations, meals, and transportation options.

## Inputs

The user must provide the following information for the planner to generate an itinerary:

- **From Location**: The departure city.
- **Start Date & End Date**: The travel dates.
- **Predefined Theme**: Adventure, relaxation, family vacation, honeymoon, etc.
- **Starting Time & Returning Time**: Preferred start and return times.
- **Group Size**: Number of travelers.
- **Total Budget**: The maximum budget for the entire trip.
- **Number of Destinations**: Number of places to visit.
- **Traveling Method**: Modes of transportation (e.g., bus, train, air, or mixed).
- **Destinations**: Name of the destination.

## Outputs

The AI Travel Planner provides a structured itinerary with the following details:

- **Destination Details**: Brief introduction and significance of each location.
- **Weather Updates**: Real-time weather conditions for morning, afternoon, and evening.
- **Transportation Recommendations**: Best travel routes and modes of transportation.
- **Budget Breakdown**: Cost estimates for activities, meals, and accommodation.
- **Accommodations**: Suggested places to stay, aligned with the user’s budget.
- **Daily Activities**: Suggested things to do each day, including sightseeing, adventure, and cultural experiences.
- **Meal Recommendations**: Dining suggestions for local cuisine and restaurants.
- **Special Events**: Information on festivals, local parties, and events.
- **Final Reflection**: Summary of the final day’s activities and departure plans.

## Sample Usage

### Example Input:
```plaintext
From Location: Chennai
Start Date: 15th September 2025
End Date: 17th September 2025
Predefined Theme: Adventure
Group Size: 2
Total Budget: ₹10,000
Number of Destinations: 1
Traveling Method: Train
Destinations: Thiruvannamalai
```

## Outputs

The AI Travel Planner provides a structured itinerary with the following details:

- **Destination Details**: Brief introduction and significance of each location.
- **Weather Updates**: Real-time weather conditions for morning, afternoon, and evening.
- **Transportation Recommendations**: Best travel routes and modes of transportation.
- **Budget Breakdown**: Cost estimates for activities, meals, and accommodation.
- **Accommodations**: Suggested places to stay, aligned with the user’s budget.
- **Daily Activities**: Suggested things to do each day, including sightseeing, adventure, and cultural experiences.
- **Meal Recommendations**: Dining suggestions for local cuisine and restaurants.
- **Special Events**: Information on festivals, local parties, and events.
- **Final Reflection**: Summary of the final day’s activities and departure plans.

### Example Output:

#### Day 1: 15th September 2025 (Monday) - Arrival & Adventure
- **Morning (8:00 AM - 12:00 PM)**:
    - **Weather Report**: Partly cloudy skies, temperature 28°C, slight chance of rain.
    - **Activity**: Depart from Chennai by train and arrive in Thiruvannamalai by noon.
    - **Accommodation**: Check into a budget-friendly guesthouse.
- **Afternoon (12:00 PM - 6:00 PM)**:
    - **Weather Report**: Hot afternoon with temperatures rising to 32°C.
    - **Activity**: Hike up Arunachala Hill for panoramic views.
    - **Lunch**: Traditional South Indian meal at a local restaurant.
- **Evening (6:00 PM - 9:00 PM)**:
    - **Weather Report**: Cool evening, light breeze, temperature 25°C.
    - **Activity**: Attend evening prayers at Annamalaiyar Temple.
    - **Dinner**: Local street food.

#### Estimated Costs:
- **Transportation**: ₹500 per person
- **Lunch**: ₹300 per person
- **Dinner**: ₹350 per person
- **Accommodation**: ₹1,000 per night

