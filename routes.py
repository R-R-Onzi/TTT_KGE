import pandas as pd
import cv2 as cv # Not actually necessary if you just want to create an image.
import numpy as np
import argparse
from os import walk
from math import radians, cos, sin, asin, sqrt
from collections import defaultdict
import itertools



def main(folder, **kwargs):
    df_trips =  pd.read_csv(f'{folder}/{kwargs["trips"]}', delimiter=",")
    df_routes = pd.read_csv(f'{folder}/{kwargs["routes"]}', delimiter=",")
    df_shapes = pd.read_csv(f'{folder}/{kwargs["shapes"]}', delimiter=",")
    df_stop_times = pd.read_csv(f'{folder}/{kwargs["stop_times"]}', delimiter=",")
    df_stops = pd.read_csv(f'{folder}/{kwargs["stops.csv"]}', delimiter=",")
    
    routes_csv: defaultdict = defaultdict(list)
    trip_csv: defaultdict = defaultdict(list)
    bus_stop_csv_true: defaultdict = defaultdict(list)
    
    df = pd.read_csv("city_areas.txt", delimiter="\t")

    min_max_lat = []
    min_max_long = []
    list_coord = []
    list_name_location = []
    long = []
    lat = []

    for i in range(df["boundary"].size):
        list_coord.extend([df["boundary"][i].replace('))', '')])
        list_coord[i] = list_coord[i].replace('POLYGON((', '')
        list_coord[i] = list_coord[i].split(',')

        for j in list_coord[i]:
            local_long, local_lat = j.split(' ')
            long.append(float(local_long))
            lat.append(float(local_lat))
        
        min_max_long.extend(long)
        min_max_lat.extend(lat)
        list_name_location.append([df['name'][i], [lat, long]])

        long = []
        lat = []

    min_long = min(min_max_long)
    max_long = max(min_max_long)
    min_lat = min(min_max_lat)
    max_lat = max(min_max_lat)
    j = 0
    for i in list_name_location:
        polygon_points = return_zip(i, (min_lat, max_lat, min_long, max_long))
        list_name_location[j][1] = polygon_points

        j = j + 1
    j = 0
    
    for trip_id in df_trips["trip_id"]:
        trip_line = df_trips.loc[df_trips['trip_id'] == trip_id]
        routes_line = df_routes.loc[df_routes['route_id'] == trip_line["route_id"].iloc[0]]
        shapes_lines = df_shapes.loc[df_shapes['shape_id'] == trip_line["shape_id"].iloc[0]]
        stop_times_line = df_stop_times.loc[df_stop_times['trip_id'] == trip_id]
    
        total_dist = 0
        for i in range(len(shapes_lines["shape_pt_lon"])):
            if (len(shapes_lines["shape_pt_lon"]) == i + 1):
                break
            
            total_dist += haversine(
                shapes_lines["shape_pt_lon"].iloc[i],
                shapes_lines["shape_pt_lat"].iloc[i],
                shapes_lines["shape_pt_lon"].iloc[i + 1],
                shapes_lines["shape_pt_lat"].iloc[i + 1],
            )

        routes_csv["route_id"].append(f"{trip_line['route_id'].iloc[0]}")
        routes_csv["distance"].append(str(total_dist))
        routes_csv["trip_id"].append(f'{trip_line["trip_id"].iloc[0]}')
        routes_csv["name"].append(f"{routes_line['route_short_name'].iloc[0]}")

        trip_csv["trip_id"].append(f'{trip_line["trip_id"].iloc[0]}')
        trip_csv["route_short_name"].append(f"{df_routes['route_short_name'].iloc[0]}")
        trip_csv["route_id"].append(f'{trip_line["route_id"].iloc[0]}')
        trip_csv["shape_id"].append(f'{trip_line["shape_id"].iloc[0]}')
        trip_csv["direction"].append(f'{trip_line["direction_id"].iloc[0]}')
        trip_csv["trip_headsign"].append(f'{trip_line["trip_headsign"].iloc[0]}')

        stop_times = df_stop_times.loc[df_stop_times['trip_id'] == f'{trip_line["trip_id"].iloc[0]}']
        bus_stop_csv: defaultdict = defaultdict(list)
        should_add = False
        for i in range(len(stop_times)):

            stop_line = df_stops.loc[df_stops["stop_id"] == int(stop_times['stop_id'].iloc[i])]
            if (len(stop_times["stop_id"]) == i + 1):
                bus_stop_csv["stop_id"].append(f"{stop_times['stop_id'].iloc[i]}")
                bus_stop_csv["route_id"].append(f"{trip_line['route_id'].iloc[0]}")
                bus_stop_csv["trip_id"].append(f'{trip_line["trip_id"].iloc[0]}')
                bus_stop_csv["next_stop_id"].append("")
                bus_stop_csv["stop_num_in_trip"].append(f"{i + 1}")
                bus_stop_csv["arrival_time"].append(f"{stop_times_line['arrival_time'].iloc[i]}")
                bus_stop_csv["departure_time"].append(f"{stop_times_line['departure_time'].iloc[i]}")
                bus_stop_csv["city_area"].append("")
                break
            next_stop_line = df_stops.loc[df_stops["stop_id"] == int(stop_times['stop_id'].iloc[i + 1])]

            point_lat = float(stop_line["stop_lat"].iloc[0])
            point_lon = float(stop_line["stop_lon"].iloc[0])
                
            if (point_lon < min_long or point_lon > max_long):
                bus_stop_csv["stop_id"].append(f"{stop_times['stop_id'].iloc[i]}")
                bus_stop_csv["route_id"].append(f"{trip_line['route_id'].iloc[0]}")
                bus_stop_csv["trip_id"].append(f'{trip_line["trip_id"].iloc[0]}')
                bus_stop_csv["next_stop_id"].append(f"{next_stop_line['stop_id'].iloc[0]}")
                bus_stop_csv["stop_num_in_trip"].append(f"{i + 1}")
                bus_stop_csv["arrival_time"].append(f"{stop_times_line['arrival_time'].iloc[i]}")
                bus_stop_csv["departure_time"].append(f"{stop_times_line['departure_time'].iloc[i]}")
                bus_stop_csv["city_area"].append("")

                continue
            point_lon = scale(point_lon, max_long, min_long)

            point_lat = float(point_lat)

            if(point_lat < min_lat or point_lat > max_lat):
                bus_stop_csv["stop_id"].append(f"{stop_times['stop_id'].iloc[i]}")
                bus_stop_csv["route_id"].append(f"{trip_line['route_id'].iloc[0]}")
                bus_stop_csv["trip_id"].append(f'{trip_line["trip_id"].iloc[0]}')
                bus_stop_csv["next_stop_id"].append(f"{next_stop_line['stop_id'].iloc[0]}")
                bus_stop_csv["stop_num_in_trip"].append(f"{i + 1}")
                bus_stop_csv["arrival_time"].append(f"{stop_times_line['arrival_time'].iloc[i]}")
                bus_stop_csv["departure_time"].append(f"{stop_times_line['departure_time'].iloc[i]}")
                bus_stop_csv["city_area"].append("")
                continue

            point_lat = scale(point_lat, max_lat, min_lat)
            scaled_point = (point_lon, point_lat)
            written = False
            for j in list_name_location:
                if (cv.pointPolygonTest(j[1], scaled_point, False) >= 0):
                    bus_stop_csv["stop_id"].append(f"{stop_times['stop_id'].iloc[i]}")
                    bus_stop_csv["route_id"].append(f"{trip_line['route_id'].iloc[0]}")
                    bus_stop_csv["trip_id"].append(f'{trip_line["trip_id"].iloc[0]}')
                    bus_stop_csv["next_stop_id"].append(f"{next_stop_line['stop_id'].iloc[0]}")
                    bus_stop_csv["stop_num_in_trip"].append(f"{i + 1}")
                    bus_stop_csv["arrival_time"].append(f"{stop_times_line['arrival_time'].iloc[i]}")
                    bus_stop_csv["departure_time"].append(f"{stop_times_line['departure_time'].iloc[i]}")
                    bus_stop_csv["city_area"].append(f"{j[0]}")
                    written = True
                    should_add = True
                    break

            if(not written):
                bus_stop_csv["stop_id"].append(f"{stop_times['stop_id'].iloc[i]}")
                bus_stop_csv["route_id"].append(f"{trip_line['route_id'].iloc[0]}")
                bus_stop_csv["trip_id"].append(f'{trip_line["trip_id"].iloc[0]}')
                bus_stop_csv["next_stop_id"].append(f"{next_stop_line['stop_id'].iloc[0]}")
                bus_stop_csv["stop_num_in_trip"].append(f"{i + 1}")
                bus_stop_csv["arrival_time"].append(f"{stop_times_line['arrival_time'].iloc[i]}")
                bus_stop_csv["departure_time"].append(f"{stop_times_line['departure_time'].iloc[i]}")
                bus_stop_csv["city_area"].append("")

        if(should_add):
            for i in range(len(bus_stop_csv["stop_id"])):
                bus_stop_csv_true["stop_id"].append(bus_stop_csv["stop_id"][i])
                bus_stop_csv_true["route_id"].append(bus_stop_csv["route_id"][i])
                bus_stop_csv_true["trip_id"].append(bus_stop_csv["trip_id"][i])
                bus_stop_csv_true["next_stop_id"].append(bus_stop_csv["next_stop_id"][i])
                bus_stop_csv_true["stop_num_in_trip"].append(bus_stop_csv["stop_num_in_trip"][i])
                bus_stop_csv_true["arrival_time"].append(bus_stop_csv["arrival_time"][i])
                bus_stop_csv_true["departure_time"].append(bus_stop_csv["departure_time"][i])
                bus_stop_csv_true["city_area"].append(bus_stop_csv["city_area"][i])
        
    pd.DataFrame(bus_stop_csv_true).to_csv("bus_stop_results.csv", index=False)
    pd.DataFrame(trip_csv).to_csv("trip_results.csv", index=False)
    pd.DataFrame(routes_csv).to_csv("routes_results.csv", index=False)


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


def scale(metrics, max, min):
    if type(metrics) is list:
        new_list = []
        for i in metrics: 
            new_list.extend([0 + (i - min) * ((6000 - 0) / (max - min))])
        return new_list
    return int(0 + (metrics - min) * ((6000 - 0) / (max - min)))

def return_zip(future_zip, thingis):

    new_list = []
    for i in range(len(future_zip[1][0])):
        new_list.append([scale(future_zip[1][1][i], thingis[3], thingis[2]), scale(future_zip[1][0][i], thingis[1], thingis[0])])

    return np.int32(new_list)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', metavar='path', required=True,
    help='folder to transporti')
    
    args = parser.parse_args()
    
    f : dict = {}
    for (dirpath, dirnames, filenames) in walk(args.folder):
        for file_name in filenames:
            if("trips" in file_name):
                f.update({"trips": file_name})

            elif("routes" in file_name):
                f.update({"routes":file_name})

            elif("shapes" in file_name):
                f.update({"shapes":file_name})
            
            elif("stop_times" in file_name):
                f.update({"stop_times":file_name})
            
            elif("stops.csv" in file_name):
                f.update({"stops.csv":file_name})
    
    assert set(("shapes", "routes", "trips", "stop_times", "stops.csv")).issubset(set(f.keys()))
                
    main(args.folder, **f)
