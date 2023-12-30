import pandas as pd

bus_stops_path = "Data/bus_stop_results.csv"
services_path = "Data/clean_services.csv"
schedules_path = "Data/schedules.csv"
locations_path = "Data/locations.csv"

bus_stops = pd.read_csv(bus_stops_path, dtype={'next_stop_id': 'Int64', 'city_area_id': 'Int64'})
services = pd.read_csv(services_path)

# SCHEDULES

merged_times = bus_stops["arrival_time"] + "|" + bus_stops["departure_time"]

schedules = []
for s in merged_times.unique():
    id = len(schedules)
    arrival_time, departure_time = s.split("|")
    schedules.append({"id": id, "arrival_time": arrival_time, "departure_time": departure_time})

schedules = pd.DataFrame(schedules)
schedules.to_csv(schedules_path, index=False)

bus_stops["schedule_id"] = bus_stops.apply(lambda x: schedules.query(f"arrival_time == '{x['arrival_time']}' and departure_time == '{x['departure_time']}'")["id"].iloc[0], axis=1)
bus_stops = bus_stops.drop(columns=["arrival_time", "departure_time"])


# LOCATIONS

locations_merged = pd.concat([bus_stops["stop_lon"].astype(str) + "|" + bus_stops["stop_lat"].astype(str),
                      services["points"].map(lambda x: x[7:-1].replace(" ", "|"))])

locations = []
for l in locations_merged.unique():
    id = len(locations)
    long, lat = l.split("|")
    locations.append({"id": id, "longitude": long, "latitude": lat})

locations = pd.DataFrame(locations)
locations.to_csv(locations_path, index=False)

bus_stops["location_id"] = bus_stops.apply(lambda x: locations.query(f"latitude == '{x['stop_lat']}' and longitude == '{x['stop_lon']}'")["id"].iloc[0], axis=1)
bus_stops = bus_stops.drop(columns=["stop_lat", "stop_lon"])

services["location_id"] = services.apply(lambda x: locations.query(f"latitude == '{x['points'][7:-1].split(' ')[1]}' and longitude == '{x['points'][7:-1].split(' ')[0]}'")["id"].iloc[0], axis=1)
services = services.drop(columns=["points"])
services = services.rename(columns={"name": "city_area_id"})

bus_stops.to_csv(bus_stops_path, index=False)
services.to_csv(services_path, index=False)