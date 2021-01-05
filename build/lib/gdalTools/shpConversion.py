import os
import gdal, gdalconst, ogr

def pol2line(polyfn, linefn):
    """
        This function is used to make polygon convert to line
    :param polyfn: the path of input, the shapefile of polygon
    :param linefn: the path of output, the shapefile of line
    :return:
    """
    driver = ogr.GetDriverByName('ESRI Shapefile')
    polyds = ogr.Open(polyfn, 0)
    polyLayer = polyds.GetLayer()
    spatialref = polyLayer.GetSpatialRef()
    #创建输出文件
    if os.path.exists(linefn):
        driver.DeleteDataSource(linefn)
    lineds =driver.CreateDataSource(linefn)
    linelayer = lineds.CreateLayer(linefn, srs=spatialref, geom_type=ogr.wkbLineString)
    featuredefn = linelayer.GetLayerDefn()
    #获取ring到几何体
    #geomline = ogr.Geometry(ogr.wkbGeometryCollection)
    for feat in polyLayer:
        geom = feat.GetGeometryRef()
        ring = geom.GetGeometryRef(0)
        #geomcoll.AddGeometry(ring)
        outfeature = ogr.Feature(featuredefn)
        outfeature.SetGeometry(ring)
        linelayer.CreateFeature(outfeature)
        outfeature = None


def poly2Raster(shp, templatePic, output, field, nodata):
    """
        making polygon shapefile convert to raster
    shp: String，the path of shapefile
    templatePic: String，the template of raster. You can get geo-information from the raster，
                the output raster should have the same size with this raster.
    output: String, the path of output shapefile
    field: the field of output you want
    nodata: The converted value of an integer or floating point vector blank
    """
    ndsm = templatePic
    data = gdal.Open(ndsm, gdalconst.GA_ReadOnly)
    geo_transform = data.GetGeoTransform()
    proj=data.GetProjection()
    #source_layer = data.GetLayer()
    # x_min = geo_transform[0]
    # y_max = geo_transform[3]
    # x_max = x_min + geo_transform[1] * data.RasterXSize
    # y_min = y_max + geo_transform[5] * data.RasterYSize
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    mb_v = ogr.Open(shp)
    mb_l = mb_v.GetLayer()
    pixel_width = geo_transform[1]
    #输出影像为16位整型
    target_ds = gdal.GetDriverByName('GTiff').Create(output, x_res, y_res, 1, gdal.GDT_Int16)

    target_ds.SetGeoTransform(geo_transform)
    target_ds.SetProjection(proj)
    band = target_ds.GetRasterBand(1)
    NoData_value = nodata
    band.SetNoDataValue(NoData_value)
    band.FlushCache()
    gdal.RasterizeLayer(target_ds, [1], mb_l, options=["ATTRIBUTE=%s"%field,'ALL_TOUCHED=TRUE'])

    target_ds = None