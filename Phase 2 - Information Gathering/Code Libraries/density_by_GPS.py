import pandas as pd
import cv2 as cv 
import numpy as np
import argparse
from os import walk
import math
from collections import defaultdict
import itertools

def main(path, files):
    
    color = [[96, 164, 244],[87, 139, 46],[238, 245, 255],[45, 82, 160],[192, 192, 192],[235, 206, 135],[205, 90, 106],[144, 128, 112],[144, 128, 112],[250, 250, 255],[127, 255, 0],[180, 130, 70],[140, 180, 210],[128, 128, 0],[216, 191, 216],[71, 99, 255],[208, 224, 64],[238, 130, 238],[179, 222, 245],[255, 255, 255],[245, 245, 245],[0, 255, 255],[50, 205, 154]] 
        
    min_max_lat = []
    min_max_long = []

    df = pd.read_csv("city_areas.txt", delimiter="\t")
    
    list_coord = []
    list_name_location = []
    long = []
    lat = []
    result_csv = defaultdict(list)
    colours = dict(zip(df["id"], itertools.count()))

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
        list_name_location.append([df['id'][i], [lat, long]])

        long = []
        lat = []

    min_long = min(min_max_long)
    max_long = max(min_max_long)
    min_lat = min(min_max_lat)
    max_lat = max(min_max_lat)
    
    blank_image = np.zeros((6000, 6000, 3), np.int32)
    j = 0
    
    for i in list_name_location:

        polygon_points = return_zip(i, (min_lat, max_lat, min_long, max_long))
        
        # for k in range(len(polygon_points)) :
            
        #     if k == len(polygon_points)- 1:
        #         blank_image = cv.line(blank_image, polygon_points[k], polygon_points[0], color[j%23], 2)
        #         break
            
        #     blank_image = cv.line(blank_image, polygon_points[k], polygon_points[k+1], color[j%23], 2)
        list_name_location[j][1] = polygon_points
        blank_image = cv.polylines(blank_image, [polygon_points], True, color[colours[i[0]]], 3)
        
        j = j + 1
        polygon_points = []

        cv.imwrite(f"{j}.jpg", blank_image)
    j = 0

    if ("bus_stop" in path):
        delim = ","
        points_parse = points_parse_separated
        aim_coord = ["stop_lat", "stop_lon"]
        dict_transform = only_coord
        append_to_dict = append_normaly

    elif ("catering" in path):
        delim = "\t"
        points_parse = points_parse_joined
        aim_coord = "coordinates"
        dict_transform = only_coord
        append_to_dict = append_normaly
    
    elif ("services"):
        delim = ";"
        points_parse = points_parse_UTM
        aim_coord = "WKT"
        dict_transform = coord_type_id
        append_to_dict = append_services

    for file in files:
        
        df_points = pd.read_csv(f"{path}/{file}", delimiter=delim)
        point_gen = points_parse(df_points, aim_coord)
        
        for point in point_gen:

            point_lat = float(point[0])
            point_lon = float(point[1])
            
            gps_point = [float(point[0]), float(point[1])]
            
            if point_lon < min_long or point_lon > max_long:
                continue
            point_lon = scale(point_lon, max_long, min_long)

            point_lat = float(point_lat)

            if point_lat < min_lat or point_lat > max_lat:
                continue
            
            point_lat = scale(point_lat, max_lat, min_lat)
            scaled_point = (point_lon, point_lat)

            result = inside_circoscrizione(list_name_location, scaled_point)
            if (result):
                result_csv = append_to_dict(result_csv, result, scaled_point, df_points, point[2], gps_point)
                blank_image = cv.circle(blank_image, scaled_point, radius=1, color=color[colours[result]], thickness=3)

    df = pd.DataFrame(dict_transform(result_csv, df))

    df.to_csv("results.csv", index=False)
    df_ca = pd.read_csv("city_areas.txt", delimiter="\t")
    results = defaultdict(list)
    result_csv
    for name in df_ca['name']:
        line = df.loc[df['name'] == name]
        line_ca = df_ca.loc[df_ca['name'] == name]
        results['name'].append(name)
        results['density'].append(len(result_csv[name]))
        results['boundary'].append(line_ca["boundary"].iloc[0])

    df = pd.DataFrame(results)
    df.to_csv("results_ca.csv", index=False)
    blank_image = cv.flip(blank_image, 0)


def append_normaly(result_csv, result, scaled_point, df=None, point=None, gps=None):
    result_csv[result].append(scaled_point)
    
    return result_csv
    
def append_services(result_csv, result, scaled_point, df, point, gps_point):
    line = df.loc[df['WKT'] == f"POINT ({point[0]} {point[1]})"]
    
    result_csv[result].append([f"{gps_point[1]} {gps_point[0]}", 
                               str(line["tipo"].iloc[0]) if line["tipo"].any(axis=None) else "",
                               str(line["nome"].iloc[0]) if line["nome"].any(axis=None) else ""])

    if (len(line["tipo"]) > 1):
        df.drop(df.loc[df['WKT'] == f"POINT ({point[0]} {point[1]})"].index[0], inplace=True)

    return result_csv

def only_coord(result_csv, df):
    results = defaultdict(list)

    for key, value in result_csv.items():
        results["name"].append(key)
        results["density"].append(len(value))
        results["points"].append(value)
    
    return results

def coord_type_id(result_csv, df):
    results = defaultdict(list)
    
    for key, value in result_csv.items():
        for place in value:
            results["id"].append(str(len(results["id"])))

            if (key):
                results["name"].append(key)
            else:
                results["name"].append("")
                
            if ("NaN"  not in place[1]):
                results["product_category"].append(place[1])
            else:
                results["product_category"].append("")
            
            if ("NaN" not in place[2] ):
                results["store_name"].append(place[2])
            else:
                results["store_name"].append("")

            if ("NaN" not in place[0]):
                results["points"].append(f"POINT ({place[0]})")
            else:
                results["points"].append("")
        
    return results

def inside_circoscrizione(list_name_location, point):

    for i in list_name_location:
        if (cv.pointPolygonTest(i[1], point, False) >= 0):
            return i[0]
    return False

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

def points_parse_separated(df_points, name):
    
    for i in range(0, df_points[name[0]].size):
        point_lat = df_points[name[0]][i]
        point_lon = df_points[name[1]][i]
    
        yield [point_lat, point_lon, None]


def points_parse_joined(df_points, name):
    
    for i in range(0, df_points[name].size):
        
        point_parsed = df_points[name][i].replace('POINT(', '').replace(')', '')
        
        [point_lat, point_lon] = point_parsed.split(' ')

        yield [point_lat, point_lon]

def points_parse_UTM(df_points, name):

    for i in range(0, df_points[name].size):
        
        point_parsed = df_points[name][i].replace('POINT (', '').replace(')', '')
        
        lat, long = point_parsed.split(' ')
        
        [point_lat, point_lon] = convert(float(lat), float(long))

        yield [point_lat, point_lon, [float(lat), float(long)]]

def convert(x, y, utmz=32):
    DatumEqRad = [6378137.0,
                        6378137.0,
                        6378137.0,
                        6378135.0,
                        6378160.0,
                        6378245.0,
                        6378206.4,
                        6378388.0,
                        6378388.0,
                        6378249.1,
                        6378206.4,
                        6377563.4,
                        6377397.2,
                        6377276.3] 
    DatumFlat = [298.2572236,
                    298.2572236,
                    298.2572215,
                    298.2597208,
                    298.2497323,
                    298.2997381,
                    294.9786982,
                    296.9993621,
                    296.9993621,
                    293.4660167,
                    294.9786982,
                    299.3247788,
                    299.1527052,
                    300.8021499] 

    Item = 0                    
    a    = DatumEqRad[Item]     
    f    = 1 / DatumFlat[Item]
    drad = math.pi / 180      


    k0   = 0.9996                     # scale on central meridian
    b    = a*(1 - f)                  # polar axis
    e    = math.sqrt(1 - (b/a)*(b/a)) # eccentricity
    e0   = e / math.sqrt(1 - e*e)     # called e' in reference
    esq  = (1 - (b/a) * (b/a))        # e² for use in expansions
    e0sq = e*e / (1 - e*e)            # e0² — always even powers

    #  Now the actual calculation:
    zcm = 3 + 6*(utmz-1) - 180  # central meridian of zone
    e1  = (1 - math.sqrt(1 - e*e)) / (1 + math.sqrt(1 - e*e)) # called e₁ in USGS PP 1395
    M0  = 0  # in case origin other than zero lat - not needed for standard UTM

    M = 0  # arc length along standard meridian

    M = M0 + y/k0

    mu = M / (a * (1 - esq*(1/4 + esq*(3/64 + 5*esq/256))))
    phi1 = mu + e1*(3/2 - 27*e1*e1/32)*math.sin(2*mu) + e1*e1*(21/16 -55*e1*e1/32)*math.sin(4*mu)  # footprint Latitude
    phi1 = phi1 + e1*e1*e1*(math.sin(6*mu)*151/96 + e1*math.sin(8*mu)*1097/512)
    C1 = e0sq * math.pow(math.cos(phi1), 2)
    T1 = math.pow(math.tan(phi1), 2)
    N1 = a / math.sqrt(1 - math.pow(e * math.sin(phi1), 2))
    R1 = N1 * (1 - e*e) / (1 - math.pow(e * math.sin(phi1), 2))
    D  = (x - 500000) / (N1*k0)
    phi = (D*D) * (1/2 - D*D * (5 + 3*T1 + 10*C1 - 4*C1*C1 - 9*e0sq) / 24)
    phi = phi + math.pow(D, 6) * (61 + 90*T1 + 298*C1 + 45*T1*T1 -252*e0sq - 3*C1*C1) / 720
    phi = phi1 - (N1 * math.tan(phi1) / R1) * phi

    # Output Latitude:
    outLat = math.floor(1000000*phi / drad) / 1000000

    lng = D * (1 + D*D * ((-1 -2*T1 -C1)/6 + D*D * (5 - 2*C1 + 28*T1 - 3*C1*C1 + 8*e0sq + 24*T1*T1) / 120)) / math.cos(phi1)
    lngd = zcm + lng/drad

    #  Output Longitude:
    outLon = math.floor(1000000*lngd)/1000000

    return [outLat, outLon]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', metavar='path', required=True,
    help='folder points')
    
    args = parser.parse_args()
    
    f = []
    for (dirpath, dirnames, filenames) in walk(args.folder):
        f.extend(filenames)
        break
    
    main(args.folder, filenames)
