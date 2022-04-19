#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# @Time : 2022/4/19 16:05 
# @Author : DKY
# @File : landsat8_to_one_tif.py
from Impervious_Surface import get_file_name
from osgeo import gdal
import numpy as np
import os
from matplotlib import pyplot as plt
def main(path, out):
    tif_list = determinate_band(path)
    g_set = gdal.Open(tif_list[1])
    geoTransform = g_set.GetGeoTransform()
    ListgeoTransform = list(geoTransform)
    ListgeoTransform[5] = -ListgeoTransform[5]
    Transform = tuple(ListgeoTransform)
    proj = g_set.GetProjection()
    cols = g_set.RasterXSize
    rows = g_set.RasterYSize
    proj1 = IDataSet.GetProjection()
    tiffile = os.path.splitext(tif_list[0])[0] + '.tif'

    tarpath = os.path.join(out, os.path.basename(tiffile))
    format = "GTiff"
    driver = gdal.GetDriverByName(format)

    bandnum = 4
    indexset = driver.Create(tarpath, cols, rows, bandnum, gdal.GDT_Int32)
    indexset.SetGeoTransform(Transform)
    indexset.SetProjection(proj1)
    for i in range(bandnum):
        ds = gdal.Open(tif_list[i])
        banddata = ds.GetRasterBand(1).ReadAsArray()
        Band = indexset.GetRasterBand(i + 1)
        Band.WriteArray(banddata, 0, 0)


def determinate_band(path):
    tif_list = get_file_name(path, 'TIF')
    try:
        for tif in tif_list:
            if os.path.splitext(tif)[0].split('_')[-1] == 'B2':
                b = tif
            if os.path.splitext(tif)[0].split('_')[-1] == 'B3':
                g = tif
            if os.path.splitext(tif)[0].split('_')[-1] == 'B4':
                r = tif
            if os.path.splitext(tif)[0].split('_')[-1] == 'B5':
                nir = tif
            if os.path.splitext(tif)[0].split('_')[-1] == 'B6':
                swir1 = tif
            if os.path.splitext(tif)[0].split('_')[-1] == 'B7':
                swir2 = tif
    except:
        print('error')

    return [b, g, r, nir, swir1, swir2]
if __name__ == '__main__':
    img = r'D:\dengkaiyuan\data\S2\LC09_L2SP_202023_20220319_20220323_02_T1'
    out = 'D:\dengkaiyuan\data\S2'
    main(img, out)