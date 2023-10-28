
import pandas as pd
import cv2 as cv # Not actually necessary if you just want to create an image.
import numpy as np

def main():
    polygon_points = []
    min_max_lat = []
    min_max_long = []

    color = [[96, 164, 244],[87, 139, 46],[238, 245, 255],[45, 82, 160],[192, 192, 192],[235, 206, 135],[205, 90, 106],[144, 128, 112],[144, 128, 112],[250, 250, 255],[127, 255, 0],[180, 130, 70],[140, 180, 210],[128, 128, 0],[216, 191, 216],[71, 99, 255],[208, 224, 64],[238, 130, 238],[179, 222, 245],[255, 255, 255],[245, 245, 245],[0, 255, 255],[50, 205, 154]]
    df = pd.read_csv("city_areas.txt", delimiter="\t")
    df_points = pd.read_csv("transport/bus_stop/point_bus_stop.txt", delimiter="\t")
    
    list_coord = []
    list_name_location = []
    
    for i in range(0,df["boundary"].size):
        list_coord.extend([df["boundary"][i].replace('))', '')])
        list_coord[i] = list_coord[i].replace('POLYGON((', '')
        list_coord[i] = list_coord[i].split(',')

    long = []
    lat = []

    for i in range(df["boundary"].size):
        for k in list_coord:

            local_long, local_lat = k[i].split(' ')
            long.append(float(local_long))
            lat.append(float(local_lat))
        list_name_location.append([df['name'][i], [long, lat]])
        min_max_long.extend(long)
        min_max_lat.extend(lat)
        
    min_long = min(min_max_long)
    max_long = max(min_max_long)
    min_lat = min(min_max_lat)
    max_lat = max(min_max_lat)

    blank_image = np.ones((6000, 6000, 3), np.int32) * 255

    for i in range(0, df_points["coordinates"].size):
        points = df_points["coordinates"][i].replace(')', '')
        points = points.replace('POINT(', '')
        points = points.split(' ')
        
        long = float(points[0])
        
        if long < min_long or long > max_long:
            continue
        long = scale(long, min_long, max_long)

        
        lat = float(points[1])

        if lat < min_lat or lat > max_lat:
            continue
        
        lat = scale(lat, min_lat, max_lat)

        blank_image = cv.circle(blank_image, (
            scale(long, min_long, max_long),
            scale(lat, min_lat, max_lat),
        ), radius=3, color=(0, 0, 0), thickness=3)
    
    cv.imwrite(f"{df['name'][7]}.jpg", blank_image)
        
    for i in range(0, df["boundary"].size):
        polygon_points = np.array(
            list(zip(scale(list_name_location[i][1][0], min_long, max_long), 
            list(scale(list_name_location[i][1][1], min_lat, max_lat)))), 
            np.int32,
        )

        blank_image = cv.polylines(blank_image, [polygon_points], True, color[i%23], 2)

    cv.imwrite(f"{df['name'][i]}.jpg", blank_image)
        

def scale(metrics, max, min):
    if metrics is list:
        new_list = []
        for i in metrics: 
            new_list.extend([((i - min) / (max - min)) * (6000 - 0) + 0])
        return new_list
    return (((metrics - min) / (max - min)) * (6000 - 0) + 0)

if __name__ == '__main__':
    
    main()
