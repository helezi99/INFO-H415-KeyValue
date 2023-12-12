import requests
import redis
import time
import json

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
            redis_client.expire("cities", 60)  # Set expiration time to 60 seconds (time to live - TTL)
            print(f"City information stored in Redis cache for {city_name}")

            return ret
    return

def fetch_quality_of_life(urban_area_name):
    # Convert to lowercase for consistency
    urban_area_name = urban_area_name.lower()

    # Check if the data is already in the cache
    cached_quality_of_life = redis_client.hget("quality_of_life", urban_area_name)
    
    if cached_quality_of_life:
        print(f"Quality of Life Scores retrieved from cache for {urban_area_name}")
        try:
            return json.loads(cached_quality_of_life)  # Deserialize the cached data
        except json.decoder.JSONDecodeError:
            print(f"Error decoding JSON for {urban_area_name}. Removing invalid data from cache.")
            redis_client.hdel("quality_of_life", urban_area_name)
            return None
    else:
        url = f"{teleport_base_url}urban_areas/slug:{urban_area_name}/scores/"
        response = requests.get(url)
        data = response.json()

        if "categories" in data:
            quality_of_life_scores = data["categories"]

            # Store the data in the cache
            try:
                redis_client.hset("quality_of_life", urban_area_name, json.dumps(quality_of_life_scores))  # Serialize before storing
                redis_client.expire("quality_of_life", 60)  # Set expiration time to 60 seconds (time to live - TTL)
                print(f"Quality of Life Scores stored in Redis cache for {urban_area_name}")
            except json.decoder.JSONDecodeError:
                print(f"Error encoding JSON for {urban_area_name}. Data not stored in cache.")

            return quality_of_life_scores
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
    print('Welcome to the Weather & Quality of Life Explorer, powered by Teleport API!')
    print("\n1. Fetch City Information")
    print("2. Fetch Quality of Life Scores")
    print("3. Show Cached Cities")
    print("4. Clear Cache")
    print("5. Exit")

def show_cached_data():
    cached_cities = redis_client.hgetall("cities")
    cached_quality_of_life = redis_client.hgetall("quality_of_life")

    if cached_cities or cached_quality_of_life:
        print("Cached Data:")
        for city_name, city_info in cached_cities.items():
            print(f"City: {city_name}")
            print(f"City Information: {city_info}")

        for urban_area_name, quality_of_life_scores in cached_quality_of_life.items():
            print(f"Urban Area: {urban_area_name}")
            print(f"Quality of Life Scores: {quality_of_life_scores}")
    else:
        print("No data cached.")

def get_cached_data():
    cached_cities = redis_client.hgetall("cities")
    cached_quality_of_life = redis_client.hgetall("quality_of_life")

    if cached_cities or cached_quality_of_life:
        return cached_cities, cached_quality_of_life
    else:
        return None, None

def show_cached_cities():
    start_time = time.time()
    cached_cities, cached_quality_of_life = get_cached_data()

    if cached_cities or cached_quality_of_life:
        print("Cached Data:")
        for city_name, city_info in cached_cities.items():
            print(f"City: {city_name}")
            print(f"City Information: {city_info}")

        for urban_area_name, quality_of_life_scores in cached_quality_of_life.items():
            print(f"Urban Area: {urban_area_name}")
            print(f"Quality of Life Scores: {quality_of_life_scores}")
    else:
        print("No data cached.")

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.5f} seconds")

def clear_cache():
    confirm = input("Are you sure you want to clear the cache? (y/n): ")
    if confirm.lower() == 'y':
        start_time = time.time()
        redis_client.delete("cities")  # Clear the city information cache
        redis_client.delete("quality_of_life")  # Clear the quality of life cache
        end_time = time.time()
        print("Cache cleared.")
        print(f"Time taken: {end_time - start_time:.5f} seconds")
    else:
        print("Cache not cleared.")

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

                start_time = time.time()
                quality_of_life_scores = fetch_quality_of_life(urban_area)
                end_time = time.time()

                if quality_of_life_scores:
                    print("Quality of Life Scores:")
                    for category in quality_of_life_scores:
                        print(f"{category['name']}: {category['score_out_of_10']}")
                    print(f"Time taken: {end_time - start_time:.5f} seconds")
                else:
                    print("Quality of life scores not available.")

            else:
                print("Unable to retrieve the list of urban areas.")

        elif choice == '3':
            show_cached_cities()

        elif choice == '4':
            clear_cache()

        elif choice == '5':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()