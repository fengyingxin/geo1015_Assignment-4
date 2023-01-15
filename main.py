import json
from _1_crop import crop
from _2_thin import thin
from _3_filt import filt
from _4_inte import inte


def set():
    parameter = {'crop':
                     {'path_source': "file/pickked.las",
                      'path_target': "file/cropped.txt",
                      # 'x_min': 191050,
                      # 'x_max': 191250,
                      'x_min': 190750,
                      'x_max': 191250,
                      # 'y_min': 351950,
                      # 'y_max': 352150,
                      'y_min': 351650,
                      'y_max': 352150,
                      'chunk_size': 100000},
                 'thin':
                     {'grid_reso': [10],
                      'thin_rate': [0.5]},
                 'filt':
                     {'res_c': 2,
                      'dis_e': -0.05,
                      'eps_z': 0.05,
                      'eps_g': 0.05,
                      'times': 1000
                      },
                 'inte':
                     {'res_c': 0.5
                      }
                 }

    with open('file/parameter.json', 'w') as f:
        json.dump(parameter, f)

    print(parameter)


def run():
    crop()
    thin()
    filt()
    inte()


def main():
    set()
    run()


if __name__ == "__main__":
    main()
