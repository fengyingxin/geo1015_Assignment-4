# The code is for cloth simulation filter
# Authors: Feng Yingxin(5692148), Gong Sicong(5711932), Rao Chengzhi(5841089)
import time
import json
import numpy as np
from scipy.spatial import KDTree


class Vertex:
    def __init__(self, dis_e, x_ori, y_ori, z_min, z_cur, mobility=True):
        self.dis_e = dis_e
        self.x_ori = x_ori
        self.y_ori = y_ori
        self.z_min = z_min
        self.z_cur = z_cur
        self.z_pre = z_cur - self.dis_e
        self.mobility = mobility

    def update(self):
        if self.z_cur < self.z_min:
            self.z_cur = self.z_min
            self.mobility = False
        else:
            tmp = self.z_cur
            self.z_cur = self.z_cur + self.dis_e
            self.z_pre = tmp


class Edge:
    def __init__(self, vertex_0: Vertex, vertex_1: Vertex, mobility=True):
        self.vertex_0 = vertex_0
        self.vertex_1 = vertex_1
        self.mobility = mobility

    def update(self):
        if not self.vertex_0.mobility and not self.vertex_1.mobility:
            self.mobility = False
        else:
            dis = self.vertex_1.z_cur - self.vertex_0.z_cur
            if not self.vertex_0.mobility and self.vertex_1.mobility:
                self.vertex_1.z_cur = self.vertex_1.z_cur + dis * (-0.875)
            elif self.vertex_0.mobility and not self.vertex_1.mobility:
                self.vertex_0.z_cur = self.vertex_0.z_cur + dis * 0.875
            else:
                self.vertex_0.z_cur = self.vertex_0.z_cur + dis * 0.5
                self.vertex_1.z_cur = self.vertex_1.z_cur + dis * (-0.5)


class Cloth:
    def __init__(self):
        self.movable_vertex = set()
        self.movable_edge = set()
        self.unmovable_vertex = set()
        self.unmovable_edge = set()
        self.del_z = 0

    def add_element(self, other):
        if isinstance(other, Vertex):
            self.movable_vertex.add(other)
        if isinstance(other, Edge):
            self.movable_edge.add(other)

    def update_vertex(self):
        for vertex in self.movable_vertex:
            if not vertex.mobility:
                self.unmovable_vertex.add(vertex)
            else:
                vertex.update()
        self.movable_vertex = self.movable_vertex - self.unmovable_vertex

    def update_edge(self):
        for edge in self.movable_edge:
            if not edge.mobility:
                self.unmovable_edge.add(edge)
            else:
                edge.update()
        self.movable_edge = self.movable_edge - self.unmovable_edge

    def update_delz(self):
        del_z = 0
        for vertex in self.movable_vertex:
            if abs(vertex.z_cur - vertex.z_pre) > del_z:
                del_z = abs(vertex.z_cur - vertex.z_pre)
        self.del_z = del_z


# Get the data of point cloud
def input_points(path_source):
    with open('file/{}'.format(path_source), mode='r') as ifile:
        all_x_points, all_y_points, all_z_points = [], [], []
        for line in ifile:
            strip = line.strip('\n')
            split = strip.split(',')
            x, y, z = float(split[0]), float(split[1]), -float(split[2])
            all_x_points.append(x), all_y_points.append(y), all_z_points.append(z)
        print("Data read !")
        kd_points = KDTree(np.vstack((all_x_points, all_y_points)).T)
        print("KDTree created!")
    return all_x_points, all_y_points, all_z_points, kd_points


# Initialize the cloth
def init_cloth(x_min, x_max, y_min, y_max, res_c, kd_points, all_z_points, dis_e):
    col_num, row_num = round((x_max - x_min) / res_c), round((y_max - y_min) / res_c)
    z_max = max(all_z_points)
    # Get the all the vertex
    lst_vertex = []
    for i in range(row_num + 1):
        y = y_min + i * res_c
        col_vertex = []
        for j in range(col_num + 1):
            x = x_min + j * res_c
            index = kd_points.query([x, y], k=1)
            z = all_z_points[index[1]]
            vertex = Vertex(dis_e, x, y, z, z_max + 1)
            col_vertex.append(vertex)
        lst_vertex.append(col_vertex)
    print("Vertex created!")

    # Get the edge of all the vertex
    lst_edge = []
    for i in range(row_num):
        for j in range(col_num):
            lst_edge.append((lst_vertex[i][j], lst_vertex[i][j + 1]))
            lst_edge.append((lst_vertex[i][j], lst_vertex[i + 1][j]))
    for i in range(row_num):
        lst_edge.append((lst_vertex[i][col_num], lst_vertex[i + 1][col_num]))
    for j in range(col_num):
        lst_edge.append((lst_vertex[row_num][j], lst_vertex[row_num][j + 1]))
    print("Edge created!")
    return lst_vertex, lst_edge


# Fill the cloth
def fill_cloth(lst_vertex, lst_edge):
    # Initialization of the cloth
    cloth = Cloth()

    # Add all the vertex to the cloth
    for col_vertex in lst_vertex:
        for vertex in col_vertex:
            cloth.add_element(vertex)
    print("Vertex added!")

    # Add all the edge to the cloth
    for edge in lst_edge:
        edge = Edge(edge[0], edge[1])
        cloth.add_element(edge)
    print("Edge added!")
    return cloth


# Output the cloth vertices
def output_cloth(path_source, all_vertex):
    with open('file/cloth_{}'.format(path_source), 'w') as ofile:
        result = ['{},{},{}'.format(vertex.x_ori, vertex.y_ori, vertex.z_cur) for vertex in all_vertex]
        result = '\n'.join(result) + '\n'
        ofile.write(result)
    print('Cloth done!')


# Output the ground points
def output_ground(path_source, all_vertex, all_x_points, all_y_points, all_z_points, eps_g):
    all_x_vertex = [vertex.x_ori for vertex in all_vertex]
    all_y_vertex = [vertex.y_ori for vertex in all_vertex]
    all_z_vertex = [vertex.z_cur for vertex in all_vertex]
    all_z_points = [-z for z in all_z_points]

    kd_cloth = KDTree(np.vstack((all_x_vertex, all_y_vertex)).T)
    points = zip(all_x_points, all_y_points, all_z_points)

    with open('file/ground_{}'.format(path_source), 'w') as ofile:
        result = []
        for point in points:
            x, y, z = point[0], point[1], point[2]
            index = kd_cloth.query([x, y], k=1)
            vertex_z = all_z_vertex[index[1]]
            if abs(z - vertex_z) < eps_g:
                result.append("{},{},{}".format(x, y, z))
        result = '\n'.join(result) + '\n'
        ofile.write(result)
    print('Ground done!')


def filt():
    # Open the parameter file
    with open('file/parameter.json', 'r') as pfile:
        parameter = json.load(pfile)
        res_c = parameter['filt']['res_c']
        dis_e = parameter['filt']['dis_e']
        eps_z = parameter['filt']['eps_z']
        eps_g = parameter['filt']['eps_g']
        times = parameter['filt']['times']
        grid_reso = parameter['thin']['grid_reso']
        thin_rate = parameter['thin']['thin_rate']
        x_min, x_max = parameter['crop']['x_min'], parameter['crop']['x_max']
        y_min, y_max = parameter['crop']['y_min'], parameter['crop']['y_max']

    # Get the input parameters
    lst_input = []

    for reso in grid_reso:
        for rate in thin_rate:
            lst_input.append({'reso': reso, 'rate': rate})

    lst_path_source = ['thin_reso_{}_rate_{}.txt'.format(input['reso'], input['rate']) for input in lst_input]

    # Get the input parameters
    for path_source in lst_path_source:
        print('Start filt {}!'.format(path_source))
        start = time.time()
        # Get the data of point cloud
        points = input_points(path_source)
        all_x_points, all_y_points, all_z_points, kd_points = points
        # Initialize the cloth
        vertex_edge = init_cloth(x_min, x_max, y_min, y_max, res_c, kd_points, all_z_points, dis_e)
        lst_vertex, lst_edge = vertex_edge[0], vertex_edge[1]
        # Fill the cloth
        cloth = fill_cloth(lst_vertex, lst_edge)

        # Run the csf
        for i in range(times):
            cloth.update_vertex()
            cloth.update_edge()
            cloth.update_delz()
            if i % 100 == 0:
                print("{:.3}% del_z:{:.3}!".format(i / times * 100, cloth.del_z))
            if cloth.del_z < eps_z:
                print("Threshold is met!")
                break

        # Reverse the z values
        all_vertex = cloth.unmovable_vertex | cloth.movable_vertex
        for vertex in all_vertex:
            vertex.z_cur = - vertex.z_cur

        # Output the cloth vertices
        output_cloth(path_source, all_vertex)

        # Output the ground points
        output_ground(path_source, all_vertex, all_x_points, all_y_points, all_z_points, eps_g)

        print("Time cost is {:.3}s!".format(time.time() - start))


def main():
    filt()


if __name__ == "__main__":
    main()
