#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# @Time : 2022/3/30 10:21 
# @Author : DKY
# @File : extract_water.py

from osgeo import gdal
import numpy as np
import os
from matplotlib import pyplot as plt


def saveTif(array, cols, rows, driver, proj, Transform, filename):
    '''

    @param array: 数据矩阵
    @param cols: 列
    @param rows: 行
    @param driver:
    @param proj: 投影
    @param Transform: 存储着栅格数据集的地理坐标信息
    @param filename: 输出文件名字
    @return:
    '''

    indexset = driver.Create(filename, cols, rows, 1, gdal.GDT_Float32)
    indexset.SetGeoTransform(Transform)
    indexset.SetProjection(proj)
    Band = indexset.GetRasterBand(1)
    Band.WriteArray(array, 0, 0)


def linear_stretch(data, num=1):
    x, y = np.shape(data)
    data_new = np.zeros(shape=(x, y))

    data_8bit = data
    data_8bit[data_8bit == -9999] = 0

    # 把数据中的nan转为某个具体数值，例如
    # data_8bit[np.isnan(data_8bit)] = 0
    d2 = np.percentile(data_8bit, num)
    u98 = np.percentile(data_8bit, 100 - num)

    maxout = 255
    minout = 0
    data_8bit_new = minout + ((data_8bit - d2) / (u98 - d2)) * (maxout - minout)
    data_8bit_new[data_8bit_new < minout] = minout
    data_8bit_new[data_8bit_new > maxout] = maxout
    data_8bit_new = data_8bit_new.astype(np.int32)

    return data_8bit_new


def linear_stretch_1(data, ):
    x, y = np.shape(data)
    data_new = np.zeros(shape=(x, y))

    data_8bit = data
    data_8bit[data_8bit == -9999] = 0

    # 把数据中的nan转为某个具体数值，例如
    # data_8bit[np.isnan(data_8bit)] = 0
    maxout = 255
    minout = 0
    data_8bit_new = data_8bit / (2 ** 16) * 255
    data_8bit_new[data_8bit_new < minout] = minout
    data_8bit_new[data_8bit_new > maxout] = maxout
    data_8bit_new = data_8bit_new.astype(np.int32)
    data_8bit[data_8bit == 0] = -9999
    return data_8bit_new


def createL9Tif(cols, rows, driver, proj, Transform, filename, bandnum):
    '''

    @param array: 数据矩阵
    @param cols: 列
    @param rows: 行
    @param driver:
    @param proj: 投影
    @param Transform: 存储着栅格数据集的地理坐标信息
    @param filename: 输出文件名字
    @return:
    '''

    indexset = driver.Create(filename, cols, rows, bandnum, gdal.GDT_UInt32)
    indexset.SetGeoTransform(Transform)
    indexset.SetProjection(proj)


def get_file_name(file_dir, type):
    """
    搜索 后缀名为type的文件  不包括子目录的文件
    #
    """
    corretion_file = []
    filelist = os.listdir(file_dir)
    for file in filelist:
        if os.path.splitext(file)[1] == type:
            corretion_file.append(os.path.join(file_dir, file))
    if corretion_file == []:
        for file in filelist:
            if os.path.splitext(file)[1] == '.' + type:
                corretion_file.append(os.path.join(file_dir, file))
    return corretion_file


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


def indexCompute(arr):
    # g^4/(nir*r)^2
    blue, green, red, nir = arr[:,:,0],arr[:,:,1],arr[:,:,2],arr[:,:,3]
    num = [-1.65968, 11.43194, -9.85259, -0.58029]  # water
    # num = [0, 1.2, -1, -0.5]
    # index = num[0] * np.divide(((green * blue) ** 2), (nir * red) ** 2) + \
    #         num[1] * np.divide((green ** 4), (nir * red) ** 2) + \
    #         num[2] * np.divide(green ** 2, (nir) ** 2) + \
    #         num[3] * np.divide(green ** 2, (red) ** 2)
    num =  [0.45008409,  0.11961939,  0.35736162, -1.76948519]   # building
    index = num[0] * np.divide(((green*blue)**2), (nir*red) ** 2) + \
            num[1] * np.divide((green**2**2), (nir*red) ** 2) + \
            num[2] * np.divide(green**2, (nir) ** 2) + \
            num[3] * np.divide(green**2, (red) ** 2)

    # index =0.45 * np.divide(((green*blue)**2), (nir*red) ** 2)+0.12* np.divide((green**2**2), (nir*red) ** 2) +0.36  * np.divide(green**2, (nir) ** 2)-1.77  * np.divide(green**2, (red) ** 2)

    # index = np.where(index < -10, -10, index)
    # index = np.where(index > 10, 10, index)

    return index


def testindexCompute(arr):
    '''
    arr incleding blue, green, red, nir,s1,s2 bands
    :return: 
    '''
    x, y, z = arr.shape
    arr_total = np.zeros((x, y))
    for i in range(z):
        arr_total = arr_total + arr[:, :, i]

    # arr_new = arr_new / z
    plt.imshow(arr_total), plt.show()
    index = np.divide(arr_total, (123 * 6))
    # index = 1.75 * green ** 2 - 1 * red ** 2 - 1.5 * nir ** 2
    # index = np.where(index < -1, -1, index)
    # index = np.where(index > 1, 1, index)
    return index

    # index = np.divide(blue*green+green**2+green*red-4.5*(red*nir),red*nir)


def read_img(path):
    tif_list = determinate_band(path)
    g_set = gdal.Open(tif_list[1])

    # attribute
    transform = g_set.GetGeoTransform()
    driver = g_set.GetDriver()
    geoTransform = g_set.GetGeoTransform()
    ListgeoTransform = list(geoTransform)
    ListgeoTransform[5] = -ListgeoTransform[5]
    newgeoTransform = tuple(ListgeoTransform)
    proj = g_set.GetProjection()

    originX = transform[0]
    originY = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    cols = g_set.RasterXSize
    rows = g_set.RasterYSize
    temp_arr = np.zeros((rows, cols, 6))
    for i in range(6):
        b_set = gdal.Open(tif_list[i])
        # b_set.SetNoDataValue(-9999)
        b = b_set.GetRasterBand(1).ReadAsArray()
        # b = np.where(b == 0, b, b)
        b = linear_stretch_1(b)

        temp_arr[:, :, i] = b

    # show = np.zeros((rows, cols, 3)).astype(np.int32)
    # show[:, :, 0] = b
    # show[:, :, 1] = g
    # show[:, :, 2] = r
    # plt.imshow(show)
    # plt.show()

    index = indexCompute(temp_arr)
    indexname = os.path.splitext(tif_list[0])[0] + '_index.tif'
    # index = np.where(index ==0,np.nan , index)
    saveTif(index, cols, rows, driver, proj, newgeoTransform, indexname)
    L9name = os.path.splitext(tif_list[0])[0] + '_superposition.tif'

    # a = np.zeros(rows, cols)
    a = index
    a = np.where(a >= 0.2, 255, a)
    a = np.where(a < 0, 9999, a)
    a = np.where(a < 1, 100, a)

    plt.imshow(a), plt.show()
    if os.path.exists(L9name) == 0:
        createL9Tif(cols, rows, driver, proj, newgeoTransform, L9name, len(tif_list))
        ds = gdal.Open(L9name, gdal.GA_Update)
        for i in range(len(tif_list)):
            dataset = gdal.Open(tif_list[i])
            data = dataset.GetRasterBand(1).ReadAsArray()
            data = linear_stretch_1(data)

            band = ds.GetRasterBand(i + 1)
            band.WriteArray(data, 0, 0)
            print('写入第%d波段' % i)

    a = 0
    return index


if __name__ == "__main__":
    path = r'X:\DengKaiYuan\L9\pole'  # 冰川
    path = r'X:\DengKaiYuan\L9\wuzhou'  # 梧州
    # # path = r'X:\DengKaiYuan\L9\马达加斯加' #马达加斯加
    # # path = r'X:\DengKaiYuan\L9\Korea' #Korea
    # #
    # path = r'X:\DengKaiYuan\L9\pole2'  # 冰川
    # path = r'X:\DengKaiYuan\L9\pole3'  # 冰川
    # path = r'X:\DengKaiYuan\L9\pole4'  # 冰川
    # # path = r'X:\DengKaiYuan\L9\pole5'  # 冰川
    a = read_img(path)
    A = 0
