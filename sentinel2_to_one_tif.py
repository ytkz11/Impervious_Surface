#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# @Time : 2022/4/19 16:05 
# @Author : DKY
# @File : sentinel2_to_one_tif.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/4/19 15:16
# @Author : DKY
# @File : read_jp2.py
from osgeo import gdal
import zipfile
import os
import cv2
import numpy as np
from tqdm import tqdm
import time
class sentinel2_to_one_tif:
    def __init__(self, InputFilePath, OutputFilePath):
        self.InputFilePath = InputFilePath
        self.OutputFilePath = OutputFilePath
        if os.path.exists(self.OutputFilePath) == 0:
            os.mkdir(self.OutputFilePath)
        self.run()

    def run(self):
        '''

        '''
        SAFE_PATH =  self.InputFilePath
        file_dir = os.path.join(self.OutputFilePath, SAFE_PATH)
        imgfile, xml = self.get_file_name(file_dir)
        # 判断1LC or 2LC
        if os.path.basename(file_dir).split('_')[1] == "MSIL1C":
            band = [1, 2, 3, 4]  #
        elif os.path.basename(file_dir).split('_')[1] == "MSIL2A":
            band = [5, 6, 7, 3]
        banddata, info = self.read_jp2(imgfile[band[0]])

        tiffile = os.path.splitext(SAFE_PATH)[0] + '.tiff'

        tarpath = os.path.join(self.OutputFilePath, os.path.basename(tiffile))

        bandnum = 4
        cols, rows, driver, proj, Transform = info[0],info[1],info[2],info[3],info[4]
        format = "GTiff"
        driver = gdal.GetDriverByName(format)
        indexset = driver.Create(tarpath, cols, rows, bandnum, gdal.GDT_Int32)
        indexset.SetGeoTransform(Transform)
        indexset.SetProjection(proj)
        for i in range(bandnum):
            banddata, info = self.read_jp2(imgfile[band[i]])
            Band = indexset.GetRasterBand(i+1)
            Band.WriteArray(banddata, 0, 0)
        time.sleep(1)





    def get_file_name(self, file_dir):
        """
        get jp2 file and MTD_TL.xml file
        :param file_dir: InputFilePath
        :return: Jp2 format list, mtd_tl. XML file
        """
        L = []
        xml = []
        for dirpath, dirnames, filenames in os.walk(file_dir):
            for file in filenames:
                if os.path.splitext(file)[1] == '.jp2':
                    if 'IMG_DATA' in dirpath:
                        if '_B' in os.path.splitext(file)[0]:
                            L.append(os.path.join(dirpath, file))
        for dirpath, dirnames, filenames in os.walk(file_dir):
            for file in filenames:
                if os.path.splitext(file)[0] == 'MTD_TL':

                    xml.append(os.path.join(dirpath, file))
        return L, xml[0]
    def read_jp2(self,file):
        """
        读取jp2格式文件
        Read jp2 format files
        """
        IDataSet = gdal.Open(file, 0)
        cols = IDataSet.RasterXSize
        rows = IDataSet.RasterYSize
        ImgBand = IDataSet.GetRasterBand(1)
        ImgRasterData = ImgBand.ReadAsArray(0, 0, cols, rows)
        driver = IDataSet.GetDriver()
        geoTransform = IDataSet.GetGeoTransform()
        ListgeoTransform = list(geoTransform)
        ListgeoTransform[5] = -ListgeoTransform[5]
        newgeoTransform = tuple(ListgeoTransform)
        proj = IDataSet.GetProjection()
        info = [cols, rows, driver, proj, newgeoTransform]

        return ImgRasterData, info
if __name__ == '__main__':
    img = r'D:\dengkaiyuan\data\S2\S2A_MSIL2A_20220416T110621_N0400_R137_T30UYC_20220416T152833\S2A_MSIL2A_20220416T110621_N0400_R137_T30UYC_20220416T152833.SAFE'
    out = 'D:\dengkaiyuan\data\S2'
    sentinel2_to_one_tif(img, out)