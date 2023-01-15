# The code is for extracting isolines from dtm files
# Authors: Feng Yingxin(5692148), Gong Sicong(5711932), Rao Chengzhi(5841089)
import numpy
import math
import csv


def get_triangles(grid_pts, row_num, col_num):
    triangles = []
    for i in range(row_num - 1):
        for j in range(col_num - 1):
            p1 = grid_pts[i][j]
            p2 = grid_pts[i + 1][j]
            p3 = grid_pts[i + 1][j + 1]
            triangles.append([p1, p2, p3])
            p1 = grid_pts[i][j]
            p2 = grid_pts[i + 1][j + 1]
            p3 = grid_pts[i][j + 1]
            triangles.append([p1, p2, p3])
    return triangles


def line_z(in_pts, interval):
    z_min = 9999
    z_max = -9999
    for z in in_pts[:, 2]:
        if z < z_min:
            z_min = z
        if z > z_max:
            z_max = z
    line_num = math.ceil((z_max - z_min) / interval)
    line_z_list = []
    z_line = math.floor(z_min)
    for i in range(line_num):
        line_z_list.append(z_line)
        z_line = z_line + interval
    return line_z_list


def pt_position(po, pd, z):
    s = (z - po[2]) / (pd[2] - po[2])
    x = po[0] + s * (pd[0] - po[0])
    y = po[1] + s * (pd[1] - po[1])
    return [x, y]


def one_isoline(triangles, z):
    segmentlist = []
    for tri in triangles:
        p1 = tri[0]
        p2 = tri[1]
        p3 = tri[2]
        # isoline is the edge or the tri
        if p1[2] == z and p2[2] == z and (p1[1] < p2[1] or (p1[1] == p2[1] and p1[0] < p2[0])):
            segmentlist.append([p1[:2], p2[:2]])
        if p2[2] == z and p3[2] == z and (p2[1] < p3[1] or (p2[1] == p3[1] and p2[0] < p3[0])):
            segmentlist.append([p2[:2], p3[:2]])
        if p3[2] == z and p1[2] == z and (p3[1] < p1[1] or (p3[1] == p1[1] and p3[0] < p1[0])):
            segmentlist.append([p3[:2], p1[:2]])
        # one end of the isoline is the vertex of the tri
        if p1[2] == z and min(p2[2], p3[2]) < z < max(p2[2], p3[2]):
            segmentlist.append([p1[:2], pt_position(p2, p3, z)])
        elif p2[2] == z and min(p3[2], p1[2]) < z < max(p3[2], p1[2]):
            segmentlist.append([p2[:2], pt_position(p3, p1, z)])
        elif p3[2] == z and min(p1[2], p2[2]) < z < max(p1[2], p2[2]):
            segmentlist.append([p3[:2], pt_position(p1, p2, z)])
        # ordinary isoline
        if min(p1[2], p2[2]) < z < max(p1[2], p2[2]) and min(p2[2], p3[2]) < z < max(p2[2], p3[2]):
            segmentlist.append([pt_position(p1, p2, z), pt_position(p2, p3, z)])
        elif min(p2[2], p3[2]) < z < max(p2[2], p3[2]) and min(p3[2], p1[2]) < z < max(p3[2], p1[2]):
            segmentlist.append([pt_position(p2, p3, z), pt_position(p3, p1, z)])
        elif min(p3[2], p1[2]) < z < max(p3[2], p1[2]) and min(p1[2], p2[2]) < z < max(p1[2], p2[2]):
            segmentlist.append([pt_position(p3, p1, z), pt_position(p1, p2, z)])
    return segmentlist


def isolines_main(infile, outfile, interval, row_num, col_num):
    in_pts = numpy.loadtxt(open(infile, "r"), delimiter=",", skiprows=1)
    grid_pts = numpy.reshape(in_pts, (row_num, col_num, 3))
    line_z_list = line_z(in_pts, interval)
    segmentlists = []
    triangles = get_triangles(grid_pts, row_num, col_num)
    for z in line_z_list:
        segmentlists.append(one_isoline(triangles, z))
    with open(outfile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y', 'z', 'id'])
        id = 0
        for i in range(len(line_z_list)):
            for line in segmentlists[i]:
                writer.writerow([line[0][0], line[0][1], line_z_list[i], id])
                writer.writerow([line[1][0], line[1][1], line_z_list[i], id])
                id = id + 1


# infile: stroring the x,y,z of pts (with 3 columns and pts_num rows); the same for the following infiles
isolines_main(infile='surface.csv', outfile='test_isolines.csv', interval=5, row_num=100, col_num=100)
