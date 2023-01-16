import time
# The code is for interpolation
# Authors: Feng Yingxin(5692148), Gong Sicong(5711932), Rao Chengzhi(5841089)
import json
import numpy as np
import startinpy
import matplotlib.pyplot as plt


def get_dt(path_source):
    with open('file/{}'.format(path_source), 'r') as ifile:
        dt = startinpy.DT()
        for line in ifile:
            strip = line.strip('\n')
            split = strip.split(',')
            x, y, z = float(split[0]), float(split[1]), float(split[2])
            dt.insert_one_pt(x, y, z)
        print("DT created!")
        return dt


def init_image(x_min, x_max, y_min, y_max, res_c):
    row_num = round((x_max - x_min) / res_c)
    col_num = round((y_max - y_min) / res_c)
    x_start, x_end = x_min + res_c, x_max - res_c
    y_start, y_end = y_min + res_c, y_max - res_c
    coor_x = np.arange(x_start, x_end, res_c)
    coor_y = np.arange(y_start, y_end, res_c)
    result = np.zeros((row_num, col_num))
    return coor_x, coor_y, result

def save_image_to_csv(coor_x,coor_y,result,path_source,res_c):
    outfile=str(path_source+'.csv')
    with open(outfile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y', 'z'])
        for row, y in enumerate(coor_y):
            for col, x in enumerate(coor_x):
                writer.writerow([x, y, result[row][col]])
                
def inte():
    # Open the parameter file
    with open('file/parameter.json', 'r') as pfile:
        parameter = json.load(pfile)
        res_c = parameter['inte']['res_c']
        x_min, x_max = parameter['crop']['x_min'], parameter['crop']['x_max']
        y_min, y_max = parameter['crop']['y_min'], parameter['crop']['y_max']
        grid_reso = parameter['thin']['grid_reso']
        thin_rate = parameter['thin']['thin_rate']

    # Get the input parameters
    lst_input = []

    for reso in grid_reso:
        for rate in thin_rate:
            lst_input.append({'reso': reso, 'rate': rate})

    lst_path_cloth = ['cloth_thin_reso_{}_rate_{}.txt'.format(input['reso'], input['rate']) for input in lst_input]
    lst_path_ground = ['ground_thin_reso_{}_rate_{}.txt'.format(input['reso'], input['rate']) for input in
                       lst_input]

    lst_path_source = lst_path_cloth + lst_path_ground
    for path_source in lst_path_source:
        print('Start inte {}!'.format(path_source))
        start = time.time()
        dt = get_dt(path_source)
        image = init_image(x_min, x_max, y_min, y_max, res_c)
        coor_x, coor_y, result = image[0], image[1], image[2]
        for row, x in enumerate(coor_x):
            for col, y in enumerate(coor_y):
                if dt.is_inside_convex_hull(x, y) is False:
                    z = None
                    result[row][col] = z
                else:
                    z = dt.interpolate_laplace(x, y)
                    result[row][col] = z
        plt.figure(figsize=(8, 6))
        plt.imshow(result)
        plt.colorbar()
        plt.title(path_source)
        plt.clim(-5, 40)

        nx, ny = coor_x.shape[0], coor_y.shape[0]
        no_labels = 5
        step_x, step_y = int(nx / (no_labels - 1)), int(ny / (no_labels - 1))
        x_positions, y_positions = np.arange(0, nx, step_x), np.arange(0, ny, step_y)  # pixel count at label position
        x_labels, y_labels = coor_x[::step_x], coor_y[::step_y]  # labels you want to see
        plt.xticks(x_positions, x_labels)
        plt.yticks(y_positions, y_labels)

        plt.show()
        print("Time cost is {:.3}s!".format(time.time() - start))
        
        save_image_to_csv(coor_x,coor_y,result,path_source,res_c)


def main():
    inte()


if __name__ == "__main__":
    main()
