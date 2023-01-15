import numpy as np
import rasterio
import matplotlib.pyplot as plt

with rasterio.open('file\image.tif') as src:
    nodata = src.nodata
    data = src.read(1)
    data[data == nodata] = np.nan
    plt.figure(figsize=(8, 6))
    plt.imshow(data)
    plt.colorbar()
    plt.title('label')
    plt.clim(-5, 40)
    plt.show()



'''
# Open the image file
with rasterio.open('file\image.tif') as src:
    # Define the crop window in x,y coordinates
    xmin, ymin, xmax, ymax = (190750, 351650, 191250, 352150)
    window = src.window(xmin, ymin, xmax, ymax)
    # Read the image data within the crop window
    data = src.read(window=window)
    # Update the metadata to reflect the new dimensions
    meta = src.meta.copy()
    meta.update({'height': data.shape[1], 'width': data.shape[2]})


# Save the cropped image to a new file
with rasterio.open('file\cropped.tif', 'w', **meta) as dst:
    dst.write(data)
'''