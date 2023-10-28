
import pandas as pd
import cv2 as cv # Not actually necessary if you just want to create an image.
import numpy as np

def main():
    
    min_max_lat = []
    min_max_long = []

    color = [[96, 164, 244],[87, 139, 46],[238, 245, 255],[45, 82, 160],[192, 192, 192],[235, 206, 135],[205, 90, 106],[144, 128, 112],[144, 128, 112],[250, 250, 255],[127, 255, 0],[180, 130, 70],[140, 180, 210],[128, 128, 0],[216, 191, 216],[71, 99, 255],[208, 224, 64],[238, 130, 238],[179, 222, 245],[255, 255, 255],[245, 245, 245],[0, 255, 255],[50, 205, 154]]
    df = pd.read_csv("city_areas.txt", delimiter="\t")
    df_points = pd.read_csv("transporti/stops.txt", delimiter=",")
    
    list_coord = []
    list_name_location = []
    long = []
    lat = []
    
    for i in range(df["boundary"].size):
        list_coord.extend([df["boundary"][i].replace('))', '')])
        list_coord[i] = list_coord[i].replace('POLYGON((', '')
        list_coord[i] = list_coord[i].split(',')
        if i == 11:
            banana = 1
        for j in list_coord[i]:
            local_long, local_lat = j.split(' ')
            long.append(float(local_long))
            lat.append(float(local_lat))
        
        min_max_long.extend(long)
        min_max_lat.extend(lat)
        list_name_location.append([df['name'][i], [long, lat]])

        long = []
        lat = []

    min_long = min(min_max_long)
    max_long = max(min_max_long)
    min_lat = min(min_max_lat)
    max_lat = max(min_max_lat)

    blank_image = np.zeros((6000, 6000, 3), np.int32)

    for i in range(0, df_points["stop_lat"].size):
        point_lat = df_points["stop_lat"][i]
        point_lon = df_points["stop_lon"][i]
        
        point_lon = float(point_lon)
        
        if point_lon < min_long or point_lon > max_long:
            continue
        point_lon = scale(point_lon, min_long, max_long)

        
        point_lat = float(point_lat)

        if point_lat < min_lat or point_lat > max_lat:
            continue
        
        point_lat = scale(point_lat, min_lat, max_lat)

        blank_image = cv.circle(blank_image, (point_lon, point_lat), radius=1, color=(255, 255, 255), thickness=3)
    
    cv.imwrite(f"{df['name'][7]}.jpg", blank_image)
    j = 0

    for i in list_name_location:

        polygon_points = return_zip(i, (min_long, max_long, min_lat, max_lat))
        
        # for k in range(len(polygon_points)) :
            
        #     if k == len(polygon_points)- 1:
        #         blank_image = cv.line(blank_image, polygon_points[k], polygon_points[0], color[j%23], 2)
        #         break
            
        #     blank_image = cv.line(blank_image, polygon_points[k], polygon_points[k+1], color[j%23], 2)

        blank_image = cv.polylines(blank_image, [polygon_points], True, color[j%23], 3)
        j = j + 1
        polygon_points = []
        
        cv.imwrite(f"{j}.jpg", blank_image)

    cv.imwrite("bana.jpg", blank_image)
        

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
        new_list.append([scale(future_zip[1][0][i], thingis[1], thingis[0]), scale(future_zip[1][1][i], thingis[3], thingis[2])])

    return np.int32(new_list)

if __name__ == '__main__':
    
    main()
