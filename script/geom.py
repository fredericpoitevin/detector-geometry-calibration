"""
Fcrystfel:
    p0/corner_x = 971.443825   (px)
    p0/corner_y = -968.331466  (px)
    p0/coffset = 0.084803      (m)
    geom.translate([1,2,3])    old + (1 um, 2 um, 3 um)

Fcalib:
    
"""



class Geometry:
    def __init__(self):
        pass 

    @staticmethod
    def calib2crystfel(fcalib=None,fcrystfel=None):
        from psgeom import camera
        if not os.path.isfile(fcalib):
            return False
        if fcrystfel is None:
            return False
        geom = camera.CompoundAreaCamera.from_psana_file(fcalib) 
        geom.to_crystfel_file(fcrystfel)
        return True

    @staticmethod
    def crystfel2calib(fcrystfel=None,fcalib=None):
        from psgeom import camera
        if not os.path.isfile(fcrystfel):
            return False
        if fcalib is None:
            return False
        geom = camera.CompoundAreaCamera.from_crystfel_file(fcrystfel) 
        geom._translation = np.array([0.,0.,0.])
        geom.to_psana_file(fcalib)
        return True

    @staticmethod
    def crystfel_shift(fcrystfel=None,fsave=None,dx_um=0.,dy_um=0.,dz_um=0.):
        ## new det center = old det center + (- dx, - dy)
        ## new det distance = old det distance + dz 
        ## return new geom
        if not os.path.isfile(fcrystfel):
            return False
        if fsave is None:
            return False
        from psgeom import camera
        geom = camera.CompoundAreaCamera.from_crystfel_file(fcrystfel)
        geom._translation = np.array([0.,0.,0.])
        geom.translate([dx_um,dy_um,dz_um])  ## (um,um,um) 
        geom.to_crystfel_file(fsave)
        return True

    @staticmethod
    def calib_shift(fcalib=None,fsave=None,dx_um=0.,dy_um=0.,dz_um=0.):
        ## new det center = old det center + (- dx, - dy)
        ## new det distance = old det distance + dz 
        ## return new geom 
        if not os.path.isfile(fcalib):
            return False
        if fsave is None:
            return False
        ## 
        from psgeom import camera
        Geometry.calib2crystfel(fcalib=fcalib,fcrystfel=".temp_temp_1.geom")
        Geometry.crystfel_shift(fcrystfel=".temp_temp_1.geom",fsave=".temp_temp_2.geom",dx_um=dx_um,dy_um=dy_um,dz_um=dz_um)
        Geometry.crystfel2calib(fcrystfel=".temp_temp_2.geom",fcalib=fsave)
        return True

    @staticmethod
    def stream_shift(fstream=None):
        ## return shift_dx,shift_dy in um
        ## the value of dx,dy means that:
        ##    new det center = old det center + (dx, -dy)
        ##    new geometry = crystfel_shift(dx_um = - dx, dy_um = dy)
        if not os.path.isfile(fstream):
            return None 

        aggrx = 0.
        aggry = 0.
        nhits = 0
        # predict_refine/det_shift x = -0.004 y = -0.002 mm
        with open(fstream,"r") as f:
            for strline in f:
                if strline.startswith("predict_refine/det_shift"):
                    shiftx = strline.split("=")[1].split("y")[0]
                    shifty = strline.split("=")[2].split("mm")[0]
                    aggrx += float(shiftx) 
                    aggry += float(shifty) 
                    nhits += 1 
        shiftx_mm = aggrx * 1. / nhits
        shifty_mm = aggry * 1. / nhits
        return shiftx_mm*1000., shifty_mm*1000.


