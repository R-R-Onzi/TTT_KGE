import csv
from rdflib import RDF, Graph, URIRef

BUSSES_RDF = './EG RDF.rdf'
BASE_URI = "http://knowdive.disi.unitn.it/etype#"

g = Graph()
g.parse(BUSSES_RDF)


bus_lines = []
trips = []
bus_stops = []

for line in g.subjects(RDF.type, URIRef(BASE_URI + "Line_GID-46379")):
    line_type = g.value(line, URIRef(BASE_URI + "has_type_GID-25142_Type-46379")).toPython()

    # take only bus transportation
    if line_type == '3':
            
        line_id = len(bus_lines)
        line_name = g.value(line, URIRef(BASE_URI + "has_name_GID-34017_Type-132")).toPython()
        line_long_name = g.value(line, URIRef(BASE_URI + "has_long_name_GID-34017_Type-46379")).toPython()
        
        bus_lines.append([line_id, f"{line_name} - {line_long_name}"])         
        
        for trip in g.objects(line, URIRef(BASE_URI + "has_trips_GID-1501_Type-46379")):            
            trip_calendar = g.value(trip, URIRef(BASE_URI + "has_calendar_GID-80596_Type-1617"))
            
            calendar_weekdays = g.value(trip_calendar, URIRef(BASE_URI + "has_weekdays_GID-80597_Type-80596")).toPython()
            # calendar start end day
            
            trip_schedules = []
            for schedule in g.objects(trip, URIRef(BASE_URI + "has_schedule_GID-34769")):
                schedule_stop_sequence = g.value(schedule, URIRef(BASE_URI + "has_stops_sequence_GID-27840_Type-34818")).toPython()
                schedule_arrival_time = g.value(schedule, URIRef(BASE_URI + "has_arrival_time_GID-80845_Type-34818")).toPython()
                
                for stop in g.objects(schedule, URIRef(BASE_URI + "has_stops_GID-5446_Type-34818")):
                    bus_stop_name = g.value(stop, URIRef(BASE_URI + "has_name_GID-34017_Type-132")).toPython()                    
                    bus_long = g.value(stop, URIRef(BASE_URI + "has_longitude_GID-46270_Type-132")).toPython()                    
                    bus_lat = g.value(stop, URIRef(BASE_URI + "has_latitude_GID-46264_Type-132")).toPython()                    

                    trip_schedules.append([schedule_stop_sequence, schedule_arrival_time, bus_stop_name, float(bus_long), float(bus_lat)])                    

            # sort by stop sequence
            trip_schedules.sort(key=lambda x: int(x[0]))
            trip_schedules = [x[1:] for x in trip_schedules] # remove stop sequence, not needed anymore

            bus_stops_offset = len(bus_stops)
            first_bus_stop = [bus_stops_offset] + trip_schedules.pop(0)
            bus_stops.append(first_bus_stop)
            for id, stop in enumerate(trip_schedules, start=1):
                bus_stop_id = bus_stops_offset + id
                bus_stops.append([bus_stop_id] + stop)

                # set next stop id
                bus_stops[bus_stop_id-1].append(bus_stop_id)
            bus_stops[-1].append(None)  # last bus_stop (for the ride/trip)

            # [ trip_id, weekdays, first_bus_stop_id ]
            trips.append([len(trips), calendar_weekdays, first_bus_stop[0]])


# save to .tsv, using tabs since I'm not sure that all the names are not containing commas

lines_file = open("./bus_lines.txt", 'w')
lines_file.write("line_id\tline_name\n")
writer = csv.writer(lines_file, delimiter='\t')
writer.writerows(bus_lines)

rides_file = open("./bus_rides.txt", 'w')
rides_file.write("trip_id\tweekdays\tfirst_bus_stop_id\n")
writer = csv.writer(rides_file, delimiter='\t')
writer.writerows(trips)

stops_file = open("./bus_stops_schedules.txt", 'w')
stops_file.write("stop_id\tarrival_time\tstop_name\tstop_longitude\tstop_latitude\tnext_stop_id\n")
writer = csv.writer(stops_file, delimiter='\t')
writer.writerows(bus_stops)