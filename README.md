
# Key Value Databases Project

INFOH415 - Advanced databses (2023/24) - ULB <br />
Team: Rana İşlek, Dionisius Mayr, Thomas Suau, Herma Elezi

<div align="center">
    <img src="https://actus.ulb.be/medias/photo/logo-universite-libre-bruxelles_1661952138925-png?ID_FICHE=19524" alt="ULB Logo" width="300"/>
</div>

<br>

## Background
The choice of the right database management system technology is crucial for the success of any application. Key value store databases have gained prominence for their efficiency in storing and retrieving objects in a simple way, they are nowadays present in the mostdiverse scenarios.

## Motivation and Objective of the Project
The goal of our project is to simulate a design decision: which Database Management System (DBMS) should be used for a certain application. To do so, we will be comparing two different technologies: traditional relational databases and key-value stores. Our objective is to prove that our chosen technology is the best for this application. Additionally, we will provide arguments for the design decisions as well as a performance benchmarkofthethree database systems being compared.

## Small Demo: Weather & Quality of Life Explorer

Background Story:
Welcome to the Weather & Quality of Life Explorer,
an sample application that helps users to explore cities around the world
and make informed decisions about where to live or visit based on weather conditions and quality of life scores.

Moreover, the main aim of the application is to help users/developers who need to fetch almost the same data
repetitively in a short time. So that rather than trying to retrieve data from API in each call, Redis improves
execution time by storing those data in cache after the first fetching from API.

Here, our API is https://developers.teleport.org/api/. It has several useful information about cities such as names, 
id's, coordinates, population, and life quality scores of existed urban areas.

In the vast landscape of city data available through the Teleport API,
we encountered a challenge—fetching and displaying information quickly and efficiently.
This is where Redis, our secret weapon, comes into play. Redis is a high-performance,
in-memory data store that acts as a cache for frequently accessed city information.

How Redis Enhances Performance:

Faster Response Times:
When a user searches for a city, our application first checks Redis for cached information.
If the data is found in Redis, the application retrieves it almost instantly, providing a seamless and swift experience for the user.
This is crucial, especially for popular cities that users inquire about frequently.

Reduced API Calls:
Redis eliminates the need for redundant API calls by storing previously fetched city data.
When a user revisits a city, the application retrieves the information from Redis instead of making a time-consuming API call.
This not only speeds up the user experience but also reduces the load on the Teleport API,
contributing to better overall system efficiency.

Improved Responsiveness:
Clearing the cache is a breeze with the option to 'Clear Cache' in the menu.
This ensures that users always get the latest information when needed.
The time taken to clear the cache is optimized, making the application responsive and reliable.

User Scenario:
Imagine you are planning to relocate, and you want to explore potential cities. You start the Weather & Quality of Life Explorer:

Fetching City Information:
You enter the name of a city, and the application quickly retrieves detailed information.
If the information is cached in Redis, you see the data almost instantly, thanks to Redis's quick access.

Quality of Life Scores:
You decide to explore the quality of life scores for an urban area.
The application presents the scores without delay, utilizing Redis to store and retrieve this valuable information efficiently.

Show Cached Cities:
Curious about the cities you've already explored? You check the 'Show Cached Cities' option.
Redis provides a list of cached cities, enhancing your ability to revisit and compare information effortlessly.

Clear Cache:
You decide to clear the cache to ensure you are always getting the latest data.
Redis efficiently handles cache clearance, maintaining the application's high responsiveness.

Conclusion:
The Weather & Quality of Life Explorer, powered by Redis, delivers a user-friendly and efficient experience.
Redis's caching capabilities significantly enhance performance, making city exploration a breeze.
Whether you are a potential resident or a curious traveler,
Redis ensures that you have the most up-to-date and accessible information at your fingertips.
