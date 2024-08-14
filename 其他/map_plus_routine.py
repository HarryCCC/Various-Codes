import folium
from folium import plugins

# Create a map centered around Singapore
sg_map = folium.Map(location=[1.3521, 103.8198], zoom_start=12)

# Day 1: Arrival
# No route needed for the first evening

# Day 2: Thursday
# Route: Fish Tail Lion -> National Museum of Singapore -> NUS Techno Edge
day2_route = [
    [1.286788, 103.854522],  # Fish Tail Lion (Merlion)
    [1.296568, 103.848762],  # National Museum of Singapore
    [1.297744, 103.770008]   # NUS Techno Edge
]
folium.PolyLine(day2_route, color="blue", weight=2.5, opacity=1).add_to(sg_map)

# Add markers
folium.Marker(day2_route[0], popup="Fish Tail Lion (Merlion)").add_to(sg_map)
folium.Marker(day2_route[1], popup="National Museum of Singapore").add_to(sg_map)
folium.Marker(day2_route[2], popup="NUS Techno Edge").add_to(sg_map)

# Day 3: Friday
# Route: Chinatown -> NUS Utown
day3_route = [
    [1.283900, 103.843592],  # Chinatown
    [1.303980, 103.774061]   # NUS Utown
]
folium.PolyLine(day3_route, color="green", weight=2.5, opacity=1).add_to(sg_map)

# Add markers
folium.Marker(day3_route[0], popup="Chinatown").add_to(sg_map)
folium.Marker(day3_route[1], popup="NUS Utown").add_to(sg_map)

# Day 4: Saturday
# Route: Gardens by the Bay -> Orchard Road -> Clarke Quay
day4_route = [
    [1.281568, 103.863613],  # Gardens by the Bay
    [1.305805, 103.831313],  # Orchard Road
    [1.290694, 103.846467]   # Clarke Quay
]
folium.PolyLine(day4_route, color="red", weight=2.5, opacity=1).add_to(sg_map)

# Add markers
folium.Marker(day4_route[0], popup="Gardens by the Bay").add_to(sg_map)
folium.Marker(day4_route[1], popup="Orchard Road").add_to(sg_map)
folium.Marker(day4_route[2], popup="Clarke Quay").add_to(sg_map)

# Day 5: Sunday
# Route: Sentosa Island -> SEA Aquarium -> Skyline Luge Sentosa
day5_route = [
    [1.249404, 103.830321],  # Sentosa Island
    [1.256142, 103.820272],  # SEA Aquarium
    [1.254144, 103.821190]   # Skyline Luge Sentosa
]
folium.PolyLine(day5_route, color="purple", weight=2.5, opacity=1).add_to(sg_map)

# Add markers
folium.Marker(day5_route[0], popup="Sentosa Island").add_to(sg_map)
folium.Marker(day5_route[1], popup="SEA Aquarium").add_to(sg_map)
folium.Marker(day5_route[2], popup="Skyline Luge Sentosa").add_to(sg_map)

# Day 6: Monday
# Route: Kampong Glam -> Haji Lane -> Sultan Mosque -> Joo Chiat Road -> East Coast Park
day6_route = [
    [1.302580, 103.859869],  # Kampong Glam
    [1.300842, 103.858438],  # Haji Lane
    [1.302935, 103.859992],  # Sultan Mosque
    [1.308150, 103.902044],  # Joo Chiat Road
    [1.297710, 103.914442]   # East Coast Park
]
folium.PolyLine(day6_route, color="orange", weight=2.5, opacity=1).add_to(sg_map)

# Add markers
folium.Marker(day6_route[0], popup="Kampong Glam").add_to(sg_map)
folium.Marker(day6_route[1], popup="Haji Lane").add_to(sg_map)
folium.Marker(day6_route[2], popup="Sultan Mosque").add_to(sg_map)
folium.Marker(day6_route[3], popup="Joo Chiat Road").add_to(sg_map)
folium.Marker(day6_route[4], popup="East Coast Park").add_to(sg_map)

# Save the map as an HTML file in the current directory
sg_map.save("singapore_trip_map_with_routes.html")

print("Map with routes has been saved successfully.")
