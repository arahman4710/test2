import re
import match
from hotel import *

#  Read in the input file and close the stream
#
def main():
    c = CSV()
    f = open("output/bftpl-hotels")
    input = f.read()
    f.close()

    # Lists separated by "`\n"(always one extra line, ignore it)
    # Function parameters separated by "@"
    # Hotels separated by "~"
    # Hotel parameters separated by ";;"

    input = c.unpack(input, "\n")
    input = input[:-1] # because of extra newline

    out = []


    if len(input) > 0:
            for area in input:
                    area = c.unpack(area, "@")

                    if len(area) == 4:
                            [hotels, states, site, board] = area

                            hotels = c.unpack(hotels, "#")
                            regions = match.get_regions(states, site)
                            points = match.get_points(states, site)
                            state_hotels = match.get_state_hotels(states)
                            #print hotels
                            #if hotels:
                            hotels = re.split("~", ";;".join(hotels))

                            print regions
                           # print hotels
                            #else:
                             #   continue
                            '''
                            for hotel in hotels:
                                    hotel = re.split(";;", hotel)
                                    print hotel
                                    results = match.match_hotel(hotel, regions, state_hotels, points, site)
                                    if (results):
                                            print results
                                            for i in range(len(results)):
                                                    results[i] = ";;".join(map(str, filter(lambda x: x != "", results[i])))
                                    else:
                                            print
                                            print "FAILED: " + str(hotel)
                                            print

                                    out = "~".join(results)
                            '''
                                 #   open("output/hotel_choices", "a").write(out + "@")

if __name__ == "__main__":
    main()