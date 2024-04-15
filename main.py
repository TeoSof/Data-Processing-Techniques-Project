import csv
import folium
import webbrowser
from geopy.distance import geodesic as GD


class Node:
    def __init__(self, lat_x, lon_y, country=None, city=None, left_child=None, right_child=None):
        self.lat_x = lat_x
        self.lon_y = lon_y
        self.country = country
        self.city = city
        self.left_child = left_child
        self.right_child = right_child


class KDTree:

    def __init__(self, root=None):
        self.root = root

    def insert_elem(self, iNode):

        if self.root is None:   # if it's the first node
            self.root = iNode
            return

        current = self.root
        level = 1   # tree level
        while True:
            if level % 2 == 0:  # if i is even then compare y
                if iNode.lon_y <= current.lon_y:
                    if current.left_child is None:  # if we are at the last node, insert
                        current.left_child = iNode
                        break
                    else:
                        current = current.left_child
                else:
                    if current.right_child is None: # if we are at the last node, insert
                        current.right_child = iNode
                        break
                    else:
                        current = current.right_child
                level += 1
            else:   # if i is odd then compare x
                if iNode.lat_x <= current.lat_x:
                    if current.left_child is None:  # if we are at the last node, insert
                        current.left_child = iNode
                        break
                    else:
                        current = current.left_child
                else:
                    if current.right_child is None:     # if we are at the last node, insert
                        current.right_child = iNode
                        break
                    else:
                        current = current.right_child
                level += 1


    def nearest_neighbor(self, target, iNode, best, depth):

        global temp_node
        temp_node = None

        tmp_target = (target.lat_x, target.lon_y) # array
        tmp_iNode = (iNode.lat_x, iNode.lon_y)  # array
        candidate = GD(tmp_target, tmp_iNode).km

        if best is None:    # first
            best = iNode
        else:
            tmp_best = (best.lat_x, best.lon_y)
            if candidate < GD(tmp_target, tmp_best).km:
                best = iNode

        if depth % 2 == 0:  # compare y
            if target.lon_y <= iNode.lon_y:
                if iNode.right_child is not None:
                    temp_node = iNode.right_child
                if iNode.left_child is not None:
                    best = self.nearest_neighbor(target, iNode.left_child, best, depth + 1)
            else:
                if iNode.left_child is not None:
                    temp_node = iNode.left_child
                if iNode.right_child is not None:
                    best = self.nearest_neighbor(target, iNode.right_child, best, depth + 1)
        else:   # compare x
            if target.lat_x <= iNode.lat_x:
                if iNode.right_child is not None:
                    temp_node = iNode.right_child
                if iNode.left_child is not None:
                    best = self.nearest_neighbor(target, iNode.left_child, best, depth + 1)
            else:
                if iNode.left_child is not None:
                    temp_node = iNode.left_child
                if iNode.right_child is not None:
                    best = self.nearest_neighbor(target, iNode.right_child, best, depth + 1)


        if depth % 2 == 0:  # compare y
            cpp = Node(target.lat_x, iNode.lon_y)   # closest point possible
            if temp_node is not None:

                tmp_target = (target.lat_x, target.lon_y)
                tmp_cpp = (cpp.lat_x, cpp.lon_y)
                tmp_best = (best.lat_x, best.lon_y)

                if GD(tmp_target, tmp_cpp).km < GD(tmp_target, tmp_best).km:  # if closest point possible < current best
                    best = self.nearest_neighbor(target, temp_node, best, depth + 1)
        else:   # compare x
            cpp = Node(iNode.lat_x, target.lon_y)   # closest point possible
            if temp_node is not None:

                tmp_target = (target.lat_x, target.lon_y)
                tmp_cpp = (cpp.lat_x, cpp.lon_y)
                tmp_best = (best.lat_x, best.lon_y)

                if GD(tmp_target, tmp_cpp).km < GD(tmp_target, tmp_best).km:  # if closest point possible < current best
                    best = self.nearest_neighbor(target, temp_node, best, depth + 1)

        return best

    def circular_range_search(self, point, radius, iNode, depth):
        global temp_node
        temp_node = None

        tmp_point = (point.lat_x, point.lon_y)
        tmp_iNode = (iNode.lat_x, iNode.lon_y)

        if GD(tmp_point, tmp_iNode).km <= radius:
            print(iNode.city, "is in the radius. ", iNode.lat_x, iNode.lon_y)
            folium.Marker(location=[iNode.lat_x, iNode.lon_y], popup=iNode.city, icon=folium.Icon(color='red')).add_to(
                my_map)

        if depth % 2 == 0:
            if point.lon_y <= iNode.lon_y:
                if iNode.left_child is not None:
                    self.circular_range_search(point, radius, iNode.left_child, depth + 1)
                if iNode.right_child is not None:
                    temp_node = iNode.right_child

            else:
                if iNode.right_child is not None:
                    self.circular_range_search(point, radius, iNode.right_child, depth + 1)
                if iNode.left_child is not None:
                    temp_node = iNode.left_child
        else:
            if point.lat_x <= iNode.lat_x:
                if iNode.left_child is not None:
                    self.circular_range_search(point, radius, iNode.left_child, depth + 1)
                if iNode.right_child is not None:
                    temp_node = iNode.right_child
            else:
                if iNode.right_child is not None:
                    self.circular_range_search(point, radius, iNode.right_child, depth + 1)
                if iNode.left_child is not None:
                    temp_node = iNode.left_child


        if depth % 2 == 0:
            cpp2 = Node(point.lat_x, iNode.lon_y)   # closest point possible
            if temp_node is not None:

                tmp_point = (point.lat_x, point.lon_y)
                tmp_cpp2 = (cpp2.lat_x, cpp2.lon_y)

                if GD(tmp_point, tmp_cpp2).km <= radius:
                    self.circular_range_search(point, radius, temp_node, depth + 1)
        else:
            cpp2 = Node(iNode.lat_x, point.lon_y)   # closest point possible
            if temp_node is not None:

                tmp_point = (point.lat_x, point.lon_y)
                tmp_cpp2 = (cpp2.lat_x, cpp2.lon_y)

                if GD(tmp_point, tmp_cpp2).km <= radius:
                    self.circular_range_search(point, radius, temp_node, depth + 1)


with open(r'Fishing Ports.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter = ';')
    next(csv_reader)        # skip first row

    kdt = KDTree()

    my_map = folium.Map(location=[37.98520100051584, 23.751189777734144], zoom_start=7)

    iNode = None
    for line in csv_reader:
        iNode = Node(line[5], line[6], line[4], line[3])

        iNode.lat_x = float(iNode.lat_x.replace(",", "."))
        iNode.lon_y = float(iNode.lon_y.replace(",", "."))

        folium.Marker(location=[iNode.lat_x, iNode.lon_y], popup=iNode.city).add_to(my_map)

        kdt.insert_elem(iNode)

    r = kdt.root    # root node
    point = Node

    print("Type 'NN' (Nearest Neighbor) or 'RS' (Range Search) or 'exit':")
    inputx = input()
    while inputx != 'NN' or inputx != 'RS' or inputx != 'exit':
        if inputx == 'NN':
            print("Type point latitude:")
            point.lat_x = input()
            print("Type point longitude:")
            point.lon_y = input()

            point.lat_x = float(point.lat_x)
            point.lon_y = float(point.lon_y)

            aNode = kdt.nearest_neighbor(point, r, None, 1)
            print("Nearest neighbor coordinates: ", aNode.country, aNode.city, aNode.lat_x, aNode.lon_y)

            folium.Marker(location=[aNode.lat_x, aNode.lon_y], popup=aNode.city, icon=folium.Icon(color='red')).add_to(
                my_map)

            folium.Marker(location=[point.lat_x, point.lon_y], popup='Starting location',
                          icon=folium.Icon(color='green')).add_to(my_map)

            folium.PolyLine([(aNode.lat_x, aNode.lon_y), (point.lat_x, point.lon_y)], color='red').add_to(my_map)

            my_map.fit_bounds([[point.lat_x, point.lon_y], [aNode.lat_x, aNode.lon_y]])

            my_map.save('my_map.html')
            webbrowser.open(('my_map.html'))

            break

        elif inputx == 'RS':
            print("Type point latitude:")
            point.lat_x = input()
            print("Type point longitude:")
            point.lon_y = input()
            print("Type radius (in km):")
            radius = input()

            point.lat_x = float(point.lat_x)
            point.lon_y = float(point.lon_y)
            radius = float(radius)

            kdt.circular_range_search(point, radius, r, 1)

            folium.Circle(location=[point.lat_x, point.lon_y], radius=(radius * 1000), color='blue', fill=True).add_to(
                my_map)  # radius in meters

            my_map.location = [point.lat_x, point.lon_y]

            my_map.save('my_map.html')
            webbrowser.open(('my_map.html'))

            break
        elif inputx == 'exit':
            print("Program stopped.")
            break
        else:
            print("Wrong input.")
            print("Type 'NN' (Nearest Neighbor) or 'RS' (Range Search) or 'exit':")
            inputx = input()