# The code is for cropping a big file into a smaller one
# Authors: Feng Yingxin(5692148), Gong Sicong(5711932), Rao Chengzhi(5841089)
import time
import laspy
import json
import numpy as np


def crop():
    # Open the parameter file
    with open('file/parameter.json', 'r') as pfile:
        parameter = json.load(pfile)
        path_source, path_target = parameter['crop']['path_source'], parameter['crop']['path_target']
        x_min, x_max = parameter['crop']['x_min'], parameter['crop']['x_max']
        y_min, y_max = parameter['crop']['y_min'], parameter['crop']['y_max']
        chunks_size = parameter['crop']['chunk_size']

    print('Start crop!')
    start = time.time()
    # Open the input file
    with laspy.open(path_source, mode='r') as ifile:
        # Open the output file
        with open(path_target, mode='w') as ofile:
            points_size = ifile.header.point_count
            # Filter over the points
            for i, chunk in enumerate(ifile.chunk_iterator(chunks_size)):
                if i % 10 == 0:
                    print("{:.3}%".format(i * chunks_size / points_size * 100))
                points = chunk[(x_min < chunk.x) & (chunk.x < x_max) & (y_min < chunk.y) & (chunk.y < y_max)]
                if len(points) != 0:
                    x, y, z = points.x, points.y, points.z
                    result = np.vstack((x, y, z)).T
                    result = np.around(result, 3)
                    result = ['{},{},{}'.format(point[0], point[1], point[2]) for point in result]
                    result = '\n'.join(result) + '\n'
                    ofile.write(result)
                else:
                    pass

    print("Time cost is {:.3}s!".format(time.time() - start))


def main():
    crop()


if __name__ == "__main__":
    main()
