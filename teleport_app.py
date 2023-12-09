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
            return {
                'id': city_info["geoname_id"],
                'name': city_info["name"],
                'coordinates': city_info["location"]["latlon"],
                'population': city_info["population"]
            }

    return None

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
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            city_name = input("Enter the name of the city: ")
            cached_city_info = redis_client.hget("cities", city_name)

            if cached_city_info:
                start_time = time.time()
                print(f"City information retrieved from cache:\n{cached_city_info}")
                end_time = time.time()
                print(f"Time taken: {end_time - start_time:.2f} seconds")
            else:
                start_time = time.time()
                city_info = fetch_city_info(city_name)
                end_time = time.time()

                if city_info:
                    redis_client.hset("cities", city_name, str(city_info))
                    print(f"City information retrieved from API:\n{city_info}")
                    print(f"Time taken: {end_time - start_time:.2f} seconds")
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
                display_quality_of_life(urban_area)
                end_time = time.time()

                print(f"Time taken: {end_time - start_time:.2f} seconds")

            else:
                print("Unable to retrieve the list of urban areas.")

        elif choice == '3':
            start_time = time.time()
            show_cached_cities()
            end_time = time.time()
            print(f"Time taken: {end_time - start_time:.2f} seconds")

        elif choice == '4':
            confirm = input("Are you sure you want to clear the cache? (y/n): ")
            if confirm.lower() == 'y':
                start_time = time.time()
                redis_client.delete("cities")  # Clear the cache
                end_time = time.time()
                print("Cache cleared.")
                print(f"Time taken: {end_time - start_time:.2f} seconds")
            else:
                print("Cache not cleared.")

        elif choice == '5':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()

