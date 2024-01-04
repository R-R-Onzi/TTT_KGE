import pandas as pd

areas_filename = "./Data/city_areas.tsv"
areas = pd.read_csv(areas_filename, dtype=str, delimiter='\t')
areas["id"] = areas["id"].apply(lambda x: "city_area_" + x)
areas.to_csv(areas_filename, sep ='\t', index=False)

schedules_filename = "./Data/schedules.csv"
schedules = pd.read_csv(schedules_filename, dtype=str)
schedules["id"] = schedules["id"].apply(lambda x: "schedule_" + x)
schedules.to_csv(schedules_filename, index=False)

locations_filename = "./Data/locations.csv"
locations = pd.read_csv(locations_filename, dtype=str)
locations["id"] = locations["id"].apply(lambda x: "location_" + x)
locations.to_csv(locations_filename, index=False)


facilities_filename = "./Data/clean_services.csv"
facilities = pd.read_csv(facilities_filename, dtype=str)
facilities["id"] = facilities["id"].apply(lambda x: "facility_" + x)
facilities["city_area_id"] = facilities["city_area_id"].apply(lambda x: "city_area_" + x if not pd.isnull(x) else "")
facilities["location_id"] = facilities["location_id"].apply(lambda x: "location_" + x)
facilities.to_csv(facilities_filename, index=False)


delays_filename = "./Data/mock_delay.csv"
delays = pd.read_csv(delays_filename, dtype=str)
delays["delay_id"] = delays["delay_id"].apply(lambda x: "delay_" + x)
delays["trip_id"] = delays["trip_id"].apply(lambda x: "bus_trip_" + x)
delays.to_csv(delays_filename, index=False)


routes_filename = "./Data/routes_results.csv"
routes = pd.read_csv(routes_filename, dtype=str)
routes["route_id"] = routes["route_id"].apply(lambda x: "bus_route_" + x)
routes["trip_id"] = routes["trip_id"].apply(lambda x: "bus_trip_" + x if not pd.isnull(x) else "")
routes.to_csv(routes_filename, index=False)


stops_filename = "./Data/bus_stop_results.csv"
stops = pd.read_csv(stops_filename, dtype=str)
stops["stop_id"] = stops["stop_id"].apply(lambda x: "bus_stop_" + x)
stops["route_id"] = stops["route_id"].apply(lambda x: "bus_route_" + x if not pd.isnull(x) else "")
stops["trip_id"] = stops["trip_id"].apply(lambda x: "bus_trip_" + x if not pd.isnull(x) else "")
stops["next_stop_id"] = stops["next_stop_id"].apply(lambda x: "bus_stop_" + x if not pd.isnull(x) else "")
stops["city_area_id"] = stops["city_area_id"].apply(lambda x: "city_area_" + x if not pd.isnull(x) else "")
stops["schedule_id"] = stops["schedule_id"].apply(lambda x: "schedule_" + x)
stops["location_id"] = stops["location_id"].apply(lambda x: "location_" + x)
stops.to_csv(stops_filename, index=False)


trips_filename = "./Data/trip_results.csv"
trips = pd.read_csv(trips_filename, dtype=str)
trips["trip_id"] = routes["trip_id"].apply(lambda x: "bus_trip_" + x)
trips["route_id"] = routes["route_id"].apply(lambda x: "bus_route_" + x if not pd.isnull(x) else "")
trips["first_bus_stop_id"] = trips["first_bus_stop_id"].apply(lambda x: "bus_stop_" + x if not pd.isnull(x) else "")
trips.to_csv(trips_filename, index=False)


trips_mock_filename = "./Data/trip_with_mock_delay.csv"
trips_mock = pd.read_csv(trips_mock_filename, dtype=str)
trips_mock["trip_id"] = trips_mock["trip_id"].apply(lambda x: "bus_trip_" + x)
trips_mock["route_id"] = trips_mock["route_id"].apply(lambda x: "bus_route_" + x if not pd.isnull(x) else "")
trips_mock["first_bus_stop_id"] = trips_mock["first_bus_stop_id"].apply(lambda x: "bus_stop_" + x if not pd.isnull(x) else "")
trips_mock["delay_id"] = trips_mock["delay_id"].apply(lambda x: "delay_" + x if not pd.isnull(x) else "")
trips_mock.to_csv(trips_mock_filename, index=False)