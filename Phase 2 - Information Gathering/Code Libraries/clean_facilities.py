import glob
import csv

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon

import matplotlib.pyplot as plt
import geopandas as gpd

CIRCOSCRIZIONI_FILE = './city_areas.txt'
OSM_PLACES_ROOT_DIR = '../../osm_place/'

entities_directories = {
    'catering': 'point_of_interest/catering/**/*.txt',
    'education_facilities': 'point_of_interest/public/education/**/*.txt',
    'tourism_destinations': 'point_of_interest/tourism/destination/**/*.txt',
    'supermarket': 'point_of_interest/shopping/supermarket/*.txt',
}

# bus stop ?

if __name__ == '__main__':

    with open(CIRCOSCRIZIONI_FILE, 'r') as areas_file:
        city_areas = list(csv.reader(areas_file, delimiter='\t'))[1:]

        all_city_polygons = []
        for region in city_areas:
            region_polygon = region[3][9:-2].split(',')

            polygon_points = []
            for p in region_polygon:
                long, lat = p.split(' ')
                polygon_points.append((float(long), float(lat)))
            
            polygon = Polygon(polygon_points)
            all_city_polygons.append(polygon)
        all_city_polygons = MultiPolygon(all_city_polygons)

    for entity_name, directory in entities_directories.items(): 
        directory = OSM_PLACES_ROOT_DIR+directory
        
        for filename in glob.glob(directory):
            
            if 'polygon' in filename:
                continue
            else:
                with open(filename, 'r') as file:
                    rows = list(csv.reader(file, delimiter='\t'))[1:]

                    for row in rows:
                        point_str = row[5][6:-1].split(' ')
                        point = Point(float(point_str[0]), float(point_str[1]))

                        if all_city_polygons.contains(point):
                            print(row)
                            
                        # p = gpd.GeoSeries(all_city_polygons)
                        # fig, ax = plt.subplots(figsize=(15, 15))
                        # p.plot(ax=ax, alpha=0.7, color="pink")
                        # gpd.GeoSeries(point).plot(ax=ax)
                        # plt.show()