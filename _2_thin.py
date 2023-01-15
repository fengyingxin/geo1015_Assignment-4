# The code is for thinning a point cloud file into different thinning rates
# Authors: Feng Yingxin(5692148), Gong Sicong(5711932), Rao Chengzhi(5841089)
import time
import json
import numpy as np


class Grid:
    def __init__(self, x_min, x_max, y_min, y_max, index):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.index = index
        self.lst_point = []


# Initialize the grids
def init_grid(x_min, y_min, col_num, row_num, reso):
    lst_grid = []
    for i in range(row_num):
        y = y_min + i * reso
        for j in range(col_num):
            x = x_min + j * reso
            grid = Grid(x, x + reso, y, y + reso, i * col_num + j)
            lst_grid.append(grid)
    del grid
    return lst_grid


# Fill the grids
def fill_grid(x_min, y_min, col_num, reso, lst_grid, line):
    split = line.split(',')
    x, y = float(split[0]), float(split[1])
    col = round((x - x_min) // reso)
    row = round((y - y_min) // reso)
    index = row * col_num + col
    grid = lst_grid[index]
    grid.lst_point.append(line)


# Thin the grids
def thin_grid(grid, rate):
    points = grid.lst_point
    points_size = len(points)
    # Thin over the points
    indice_thin = np.random.choice(points_size, round(points_size * rate), replace=False)
    points_thin = [points[index] for index in indice_thin]
    return points_thin


def thin():
    # Open the parameter file
    with open('file/parameter.json', 'r') as pfile:
        parameter = json.load(pfile)
        path_source = parameter['crop']['path_target']
        grid_reso = parameter['thin']['grid_reso']
        thin_rate = parameter['thin']['thin_rate']
        x_min, x_max = parameter['crop']['x_min'], parameter['crop']['x_max']
        y_min, y_max = parameter['crop']['y_min'], parameter['crop']['y_max']

    # Get the output parameters
    list_output = []

    for reso in grid_reso:
        for rate in thin_rate:
            list_output.append({'reso': reso, 'rate': rate})

    for output in list_output:
        print('Start thin {}!'.format(output))
        start = time.time()
        reso = output['reso']
        rate = output['rate']
        print(reso, rate)

        # Initialize the grids
        col_num, row_num = round((x_max - x_min) / reso), round((y_max - y_min) / reso)
        lst_grid = init_grid(x_min, y_min, col_num, row_num, reso)

        # Open the input file
        with open(path_source, mode='r') as ifile:
            for line in ifile:
                # Fill the grids
                fill_grid(x_min, y_min, col_num, reso, lst_grid, line)

        # Open the output files
        with open("file/thin_reso_{}_rate_{}.txt".format(reso, rate), mode='w') as ofile:
            for grid in lst_grid:
                # Thin the grids
                result = thin_grid(grid, rate)
                result = ''.join(result)
                ofile.write(result)

        print("Time cost is {:.3}s!".format(time.time() - start))


def main():
    thin()


if __name__ == "__main__":
    main()
