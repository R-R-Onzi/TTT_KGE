
import pandas as pd
import cv2 as cv # Not actually necessary if you just want to create an image.
import numpy as np
import argparse
from os import walk
import math

def main(path, files):
    
    color = [[96, 164, 244],[87, 139, 46],[238, 245, 255],[45, 82, 160],[192, 192, 192],[235, 206, 135],[205, 90, 106],[144, 128, 112],[144, 128, 112],[250, 250, 255],[127, 255, 0],[180, 130, 70],[140, 180, 210],[128, 128, 0],[216, 191, 216],[71, 99, 255],[208, 224, 64],[238, 130, 238],[179, 222, 245],[255, 255, 255],[245, 245, 245],[0, 255, 255],[50, 205, 154]] 
        
    min_max_lat = []
    min_max_long = []

    df = pd.read_csv("city_areas.txt", delimiter="\t")
    
    list_coord = []
    list_name_location = []
    long = []
    lat = []
    result_csv = []

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
    
    blank_image = np.zeros((6000, 6000, 3), np.int32)
    j = 0
    
    for i in list_name_location:

        polygon_points = return_zip(i, (min_lat, max_lat, min_long, max_long))
        
        result_csv.update([{"name" : list_name_location[i][0], "polygon" : polygon_points}])
        
        # for k in range(len(polygon_points)) :
            
        #     if k == len(polygon_points)- 1:
        #         blank_image = cv.line(blank_image, polygon_points[k], polygon_points[0], color[j%23], 2)
        #         break
            
        #     blank_image = cv.line(blank_image, polygon_points[k], polygon_points[k+1], color[j%23], 2)

        blank_image = cv.polylines(blank_image, [polygon_points], True, color[j%23], 3)
        
        j = j + 1
        polygon_points = []

        cv.imwrite(f"{j}.jpg", blank_image)
        
    
    cv.imwrite(f"in.jpg", blank_image)

    if ("bus_stops" in path):
        delim = ","
        points_parse = points_parse_separated
        aim_coord = ["stop_lat", "stop_lon"]

    elif ("catering" in path):
        delim = "\t"
        points_parse = points_parse_joined
        aim_coord = "coordinates"
    
    elif ("services"):
        delim = ";"
        points_parse = points_parse_UTM
        aim_coord = "WKT"

    for file in files:
        
        df_points = pd.read_csv(f"{path}/{file}", delimiter=delim)
        point_gen = points_parse(df_points, aim_coord)
        
        for point in point_gen:

            point_lat = float(point[0])
            point_lon = float(point[1])
            
            if point_lon < min_long or point_lon > max_long:
                continue
            point_lon = scale(point_lon, max_long, min_long)

            point_lat = float(point_lat)

            if point_lat < min_lat or point_lat > max_lat:
                continue
            
            point_lat = scale(point_lat, max_lat, min_lat)

            blank_image = cv.circle(blank_image, (point_lon, point_lat), radius=1, color=(255, 255, 255), thickness=3)
            
            try_to_find_circo(list_name_location, (point_lon, point_lat))

        j = 0
        
    df = pd.DataFrame()

    df.to_csv(index=False)

    cv.imwrite("bana.jpg", blank_image)
    blank_image = cv.flip(blank_image, 0)
    cv.imwrite("normal.jpg", blank_image)

def try_to_find_circo(list_name_location, point):
    
    for (name, poly) in list_name_location:
        if (cv.pointPolygonTest(point, poly[1], False) <= 0):
            return poly

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
    
        yield [point_lat, point_lon]


def points_parse_joined(df_points, name):
    
    for i in range(0, df_points[name].size):
        
        point_parsed = df_points[name][i].replace('POINT(', '').replace(')', '')
        
        [point_lat, point_lon] = point_parsed.split(' ')

        yield [point_lat, point_lon]

def points_parse_UTM(df_points, name):

    for i in range(0, df_points[name].size):
        
        point_parsed = df_points[name][i].replace('POINT (', '').replace(')', '')
        
        lat, long = point_parsed.split(' ')
        
        [point_lat, point_lon] = convert(float(long), float(lat))

        yield [point_lat, point_lon]

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
