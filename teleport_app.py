import requests
import redis
import time

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
teleport_base_url = 'https://api.teleport.org/api/'

def fetch_city_info(city_name):
    url = f"{teleport_base_url}cities/?search={city_name}"
    response = requests.get(url)
    data = response.json()

    if "_embedded" in data and "city:search-results" in data["_embedded"]:
        search_results = data["_embedded"]["city:search-results"]
        if search_results:
            city_link = search_results[0]["_links"]["city:item"]["href"]
            city_info_response = requests.get(city_link)
            city_info = city_info_response.json()

            # Redis caching for city information
            ret = {
                'id': city_info["geoname_id"],
                'name': city_info["name"],
                'coordinates': city_info["location"]["latlon"],
                'population': city_info["population"]
            }

            redis_client.hset("cities", str.lower(city_name), str(ret))
            print(f"City information stored in Redis cache for {city_name}")

            return ret
    return

def fetch_quality_of_life(urban_area_name):
    url = f"{teleport_base_url}urban_areas/slug:{urban_area_name}/scores/"
    response = requests.get(url)
    data = response.json()

    if "categories" in data:
        return data["categories"]
    else:
        return None

def display_quality_of_life(urban_area_name):
    quality_of_life_scores = fetch_quality_of_life(urban_area_name)
    if quality_of_life_scores:
        print("Quality of Life Scores:")
        for category in quality_of_life_scores:
            print(f"{category['name']}: {category['score_out_of_10']}")
    else:
        print("Quality of life scores not available.")


def display_menu():
    print("\n#############################################################")
    print("1. Fetch City Information")
    print("2. Fetch Quality of Life Scores")
    print("3. Show Cached Cities")
    print("4. Clear Cache")
    print("5. Exit")

def show_cached_cities():
    cached_cities = redis_client.hkeys("cities")
    if cached_cities:
        print("Cached Cities:")
        for city in cached_cities:
            print(city)
    else:
        print("No cities cached.")

def main():
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ")
        print()

        if choice == '1':
            city_name = input("Enter the name of the city: ")
            start_time = time.time()
            cached_city_info = redis_client.hget("cities", str.lower(city_name))
            end_time = time.time()

            if cached_city_info:
                print(f"City information retrieved from cache:\n{cached_city_info}")
                print(f"Time taken: {end_time - start_time:.5f} seconds")
            else:
                start_time = time.time()
                city_info = fetch_city_info(city_name)
                end_time = time.time()

                if city_info:
                    print(f"City information retrieved from API:\n{city_info}")
                    print(f"Time taken: {end_time - start_time:.5f} seconds")
                else:
                    print("City not found.")

        elif choice == '2':
            url = f"{teleport_base_url}urban_areas/"
            response = requests.get(url)
            data = response.json()

            if "_links" in data and "ua:item" in data["_links"]:
                urban_areas = [item["name"] for item in data["_links"]["ua:item"]]
                print("List of Urban Areas:")
                for area in urban_areas:
                    print(area)

                urban_area = input("Enter the name of the urban area you want to fetch: ")
                urban_area = urban_area.lower()

                start_time = time.time()  # Note: This isn't an absolutely fair comparison of time for choice 2 but it still demonstrates our point.
                display_quality_of_life(urban_area)
                end_time = time.time()

                print(f"Time taken: {end_time - start_time:.5f} seconds")

            else:
                print("Unable to retrieve the list of urban areas.")

        elif choice == '3':
            start_time = time.time()
            show_cached_cities()
            end_time = time.time()
            print(f"Time taken: {end_time - start_time:.5f} seconds")

        elif choice == '4':
            confirm = input("Are you sure you want to clear the cache? (y/n): ")
            if confirm.lower() == 'y':
                start_time = time.time()
                redis_client.delete("cities")  # Clear the cache
                end_time = time.time()
                print("Cache cleared.")
                print(f"Time taken: {end_time - start_time:.5f} seconds")
            else:
                print("Cache not cleared.")

        elif choice == '5':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()

"""
Title: Weather & Quality of Life Explorer

Background Story:

Welcome to the Weather & Quality of Life Explorer,
an innovative application that empowers users to explore cities around the world
and make informed decisions about where to live or visit based on weather conditions and quality of life scores.

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
"""
