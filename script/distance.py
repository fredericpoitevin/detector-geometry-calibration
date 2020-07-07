import os,sys
import numpy as np

PATH = os.path.realpath(__file__+"/../../")
if PATH not in sys.path:
    sys.path.append(PATH)
from script.indexer import IndexPsana


class Distance:
    def __init__(self,cxiList=None,lstList=None,fcell=None,fcrystfel=None):
        self.cxiList = cxiList
        self.lstList = lstList
        self.fcell = fcell
        self.fcrystfel = fcrystfel

    def optimzie(self):
        # 1. fast scan to get the rough geometry

        # 2. fast scan to all (by blocks), log indexed to a lst file

        # 3. when log file is 100, then fine scan on center

        # 4. when log file is 500, then fine scan on distance



    @staticmethod
    def optimize_fast_scan(cxiList=None,lstList=None,fcell=None,fcrystfel=None,\
                        center_scan_range_px=100, center_scan_step_px=5,\
                        distz_scan_range_mm=100, distz_scan_step_mm=5):
        # stop whenever it found something indexed
        # get top 100 best images for indexing
        counter = 0
        indexed = False
        scanmap = []
        for center_shift_px in range(0,center_scan_range_px,center_scan_step_px):
            for distz_shift_mm in range(0,distz_scan_range_mm,distz_scan_step_mm):
                # center_shift_px = +/-5; distz_shift_mm = +/- 3mm
                lstfiles = IndexPsana(cxiList=cxiList,lstList=lstList,fcell=fcell,outDir="./temp").top(100)
                fcrystfel = Geometry.crystfelshift()
                index.fcrystfel = fcrystfel
                index.launch()
                scanmap.append([center_shift_px,distz_shift_mm,index])
                counter += 1
                if counter == 5:
                    index.wait()
                    counter = 0

                if indexed:
                    return scanmap[idx][2].fcrystfel

        if counter > 0:
            index.wait()
        return 

    @staticmethod
    def optimize_scan():
        # scan and get map 
        return 

    @staticmethod
    def optimize_center():
        # optimize the center many times
        return 

    @staticmethod
    def optimize_distz():
        # optimize the distz 
        return 

