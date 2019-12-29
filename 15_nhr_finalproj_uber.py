'''
CMPE 365 FINAL PROJECT // UBER // NATALIE RANTA // 10195854
----------------------------------------------------------------
The following Algorithm provides an optimized solution for minimizing wait times of passengers using an Uber service.
The networks of streets within a city are represented as a weighted graph data structure with weights being  time to get between nodes (locations).
A queue data structure is used to store requests which contain a timestamp, starting location and destination

Uber drivers fulfill request in order of time stamp; drivers move to pickup location & take passengers to finish location they requested,
and then fulfill the next outstanding request until the queue is empty

**NOTE: the second dataset was missing the final timestamp -- this code uses a version where the final row is removed**
'''

import networkx as nx
import pandas as pd
import time
import numpy as np

class Driver:
    # driver is given a location, and time when next available

    def __init__(self, location):
        self.location = location
        self.free_next = 0

class PriorityQueue(object):

    # priority queue is used to store requests

    def __init__(self):
        self.queue = []

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    # check if the queue is empty
    def isEmpty(self):
        return len(self.queue) == 0

    # push into the queue
    def push(self, item):
        self.queue.append(item)

    # pop element based on priority
    def pop(self):

        try:
            max = 0
            i=0
            for i in range(len(self.queue)):
                if self.queue[i] < self.queue[max]:
                    max = i
                i += 1
            item = self.queue[max]
            del self.queue[max]
            return item
        except IndexError:
            print(), exit()

def getPassengers(pq, graph):

    '''
    Algorithm for picking up/dropping off pasengers:
    Both cars look at the request at the top of the queue
    car is chosen to take passenger based on time free next and proximity to passenger
    '''

    t_wait = 0 # wait time initialized to zero
    paths = {} # store previously traversed paths here for optimization

    # initiate the two drivers
    driver1 = Driver(np.random.randint(0, 49))
    driver2 = Driver(np.random.randint(0, 49))
    passengers = 0

    while pq.isEmpty() == False:
        t = 0

        callTime = pq.queue[0][0]
        # timestamp on request
        nextPassengerLoc = pq.queue[0][1]
        # location of passenger to pick up
        nextPassengerDest = pq.queue[0][2]
        # destination of passenger to pick up

        toPassenger1 = shortestPath(graph, driver1.location, nextPassengerLoc, paths) # to passenger from car 1
        toPassenger2 = shortestPath(graph, driver2.location, nextPassengerLoc, paths) # to passenger from car 2

        # send driver 1
        if (toPassenger1 + driver1.free_next) < (toPassenger2 + driver2.free_next):

            print("Driver 1 sent! Requests:\n", pq.queue)
            driver1.free_next += toPassenger1 + shortestPath(graph, nextPassengerLoc, nextPassengerDest, paths)
            if driver1.free_next < callTime:
                driver1.free_next = callTime

            driver1.location = nextPassengerDest
            t_wait += driver1.free_next + toPassenger1 - callTime
            print("driver 1 location:", driver1.location, "\ntime to next passenger:", toPassenger1, "\nTime to dropoff:", shortestPath(graph, nextPassengerLoc, nextPassengerDest, paths), "\ndriver 1 free next: t=",driver1.free_next, "\n \n")
            passengers += 1

        # send driver 2
        else:

            print("Driver 2 sent! Requests:\n", pq.queue)
            driver2.free_next += toPassenger2 + shortestPath(graph, nextPassengerLoc, nextPassengerDest, paths)
            if driver2.free_next < callTime:
                driver2.free_next = callTime

            driver2.location = nextPassengerDest
            t_wait += driver2.free_next + toPassenger2 - callTime
            print("driver 2 location:", driver2.location, "\ntime to next passenger:", toPassenger2, "\ntime to dropoff:", shortestPath(graph, nextPassengerLoc, nextPassengerDest, paths), "\ndriver 2 free next: t=", driver2.free_next, "\n \n")
            passengers += 1
        pq.pop()

    print("passengers waited:", t_wait, "seconds total")
    print("total passengers:", passengers)
    # feel free to comment out print statements -- mainly for testing

def getRequests():
    # gets requests and stores in array
    requests = pd.read_csv('supplementpickups.csv', header=None)
    requests.columns = ["timeStamp", "pickUp", "dropOff"]
    requests.pickUp = requests.pickUp.apply(lambda x: x - 1)    # so indices match graph
    requests.dropOff = requests.dropOff.apply(lambda x: x - 1)  # so indices match graph
    return requests

def shortestPath(graph,s, t, paths):
    # Uses dynamic approach to calculate the time between paths
    # stores previously traversed paths in a dictionary
    if (s, t) in paths:
        return paths.get((s, t))
    else:
        path_length = nx.dijkstra_path_length(graph, s, t)
        paths[(s, t)] = path_length
        paths[(t, s)] = path_length
        return path_length

def main():

    g = nx.from_numpy_matrix(pd.read_csv("network.csv", header=None).as_matrix())
    q = PriorityQueue()
    requests = getRequests()

    # push the requests onto the queue
    for i in range(0, len(requests.timeStamp)):
        q.push(tuple(requests.iloc[i]))

    getPassengers(q, g)

main()


