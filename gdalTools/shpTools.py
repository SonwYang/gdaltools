from pathlib import Path
import ogr
import gdal
import os


def intersection(ShpA, ShpB, fname):
    """
    This function is used to get the intersection between shapefile A and shapefile B.
    :param shpPath: the path of input shapefile A
    :param roadShp: the path of input shapefile B
    :param fname: the path of output shapefile
    :return:
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSourceA = driver.Open(ShpA, 1)
    layerA = dataSourceA.GetLayer()

    dataSourceB = driver.Open(ShpB, 1)
    layerB = dataSourceB.GetLayer()

    # 新建DataSource，Layer
    out_ds = driver.CreateDataSource(fname)
    out_lyr = out_ds.CreateLayer(fname, layerA.GetSpatialRef(), ogr.wkbPolygon)
    def_feature = out_lyr.GetLayerDefn()
    # 遍历原始的Shapefile文件给每个Geometry做Buffer操作
    # current_union = layer[0].Clone()
    print('the length of layer:', len(layerA))
    if len(layerA) == 0:
        return

    for featureA in layerA:
        geometryA = featureA.GetGeometryRef()
        for featureB in layerB:
            geometryB = featureB.GetGeometryRef()
            inter = geometryB.Intersection(geometryA).Clone()
            out_feature = ogr.Feature(def_feature)
            out_feature.SetGeometry(inter)
            out_lyr.ResetReading()
            out_lyr.CreateFeature(out_feature)
    del dataSourceA, dataSourceB, out_ds


def MergeOneShp(inShp, outShp):
    """
        merge all features in one shapefile
    :param inShp: the path of input shapefile
    :param outShp: the path of output shapefile
    :return:
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(inShp, 1)
    layer = dataSource.GetLayer()

    # 新建DataSource，Layer
    out_ds = driver.CreateDataSource(outShp)
    out_lyr = out_ds.CreateLayer(outShp, layer.GetSpatialRef(), ogr.wkbPolygon)
    def_feature = out_lyr.GetLayerDefn()
    # 遍历原始的Shapefile文件给每个Geometry做Buffer操作
    # current_union = layer[0].Clone()
    print('the length of layer:', len(layer))
    if len(layer) == 0:
        return

    for i, feature in enumerate(layer):
        geometry = feature.GetGeometryRef()
        if i == 0:
            current_union = geometry.Clone()
        current_union = current_union.Union(geometry).Clone()

        if i == len(layer) - 1:
            out_feature = ogr.Feature(def_feature)
            out_feature.SetGeometry(current_union)
            out_lyr.ResetReading()
            out_lyr.CreateFeature(out_feature)

    del dataSource, out_ds


def multipoly2singlepoly(inputshp, outputshp):
    """
        multi part to single part
    :param inputshp: the path of input shapefile
    :param outputshp: the path of output shapefile
    :return:
    """
    gdal.UseExceptions()
    driver = ogr.GetDriverByName('ESRI Shapefile')
    in_ds = driver.Open(inputshp, 0)
    in_lyr = in_ds.GetLayer()
    if os.path.exists(outputshp):
        driver.DeleteDataSource(outputshp)
    out_ds = driver.CreateDataSource(outputshp)
    out_lyr = out_ds.CreateLayer('poly', in_lyr.GetSpatialRef(), geom_type=ogr.wkbPolygon)
    for in_feat in in_lyr:
        geom = in_feat.GetGeometryRef()
        if geom.GetGeometryName() == 'MULTIPOLYGON':
            for geom_part in geom:
                addPolygon(geom_part.ExportToWkb(), out_lyr)
        else:
            addPolygon(geom.ExportToWkb(), out_lyr)
    del in_ds, out_ds


def addPolygon(simplePolygon, out_lyr):
    featureDefn = out_lyr.GetLayerDefn()
    polygon = ogr.CreateGeometryFromWkb(simplePolygon)
    out_feat = ogr.Feature(featureDefn)
    out_feat.SetGeometry(polygon)
    out_lyr.CreateFeature(out_feat)
    print('Polygon added.')


def remove_big_feature(inputShp, outputShp, area_threshold):
    """
    This function is used to remove big area of feature from shapefile
    :param inputShp: the path of input shapefile
    :param outputShp: the path of output shapefile
    :param area_thresold: the threshold of area
    :return:
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(inputShp, 1)
    layer = dataSource.GetLayer()
    new_field = ogr.FieldDefn("Area", ogr.OFTReal)
    new_field.SetWidth(32)
    new_field.SetPrecision(16)  # 设置面积精度,小数点后16位
    layer.CreateField(new_field)

    # 新建DataSource，Layer
    out_ds = driver.CreateDataSource(outputShp)
    out_lyr = out_ds.CreateLayer(outputShp, layer.GetSpatialRef(), ogr.wkbPolygon)
    def_feature = out_lyr.GetLayerDefn()

    for feature in layer:
        geom = feature.GetGeometryRef()
        area = geom.GetArea()  # 计算面积
        if area > area_threshold:
            continue
        feature.SetField("Area", area)  # 将面积添加到属性表中
        layer.SetFeature(feature)
        out_feature = ogr.Feature(def_feature)
        out_feature.SetGeometry(geom)
        out_lyr.CreateFeature(out_feature)
        out_feature = None

    out_ds.FlushCache()
    del dataSource, out_ds


def remove_small_feature(inputShp, outputShp, area_threshold):
    """
    This function is used to remove small area of feature from shapefile
    :param inputShp: the path of input shapefile
    :param outputShp: the path of output shapefile
    :param area_thresold: the threshold of area
    :return:
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(inputShp, 1)
    layer = dataSource.GetLayer()
    new_field = ogr.FieldDefn("Area", ogr.OFTReal)
    new_field.SetWidth(32)
    new_field.SetPrecision(16)  # 设置面积精度,小数点后16位
    layer.CreateField(new_field)

    # 新建DataSource，Layer
    out_ds = driver.CreateDataSource(outputShp)
    out_lyr = out_ds.CreateLayer(outputShp, layer.GetSpatialRef(), ogr.wkbPolygon)
    def_feature = out_lyr.GetLayerDefn()

    for feature in layer:
        geom = feature.GetGeometryRef()
        area = geom.GetArea()  # 计算面积
        if area < area_threshold:
            continue
        feature.SetField("Area", area)  # 将面积添加到属性表中
        layer.SetFeature(feature)
        out_feature = ogr.Feature(def_feature)
        out_feature.SetGeometry(geom)
        out_lyr.CreateFeature(out_feature)
        out_feature = None

    out_ds.FlushCache()
    del dataSource, out_ds


def buffer(inShp, outShp, bdistance=0.02):
    """
        setting up buffer zone in shapefile
    :param inShp: the path of input shapefile
    :param outShp: the path of output shapefile
    :param bdistance: the distance of buffer
    :return:
    """
    ogr.UseExceptions()
    in_ds = ogr.Open(inShp)
    in_lyr = in_ds.GetLayer()
    # 创建输出Buffer文件
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if Path(outShp).exists():
        driver.DeleteDataSource(outShp)
    # 新建DataSource，Layer
    out_ds = driver.CreateDataSource(outShp)
    out_lyr = out_ds.CreateLayer(outShp, in_lyr.GetSpatialRef(), ogr.wkbPolygon)
    def_feature = out_lyr.GetLayerDefn()

    # 遍历原始的Shapefile文件给每个Geometry做Buffer操作
    for feature in in_lyr:
        geometry = feature.GetGeometryRef()
        buffer = geometry.Buffer(bdistance)
        out_feature = ogr.Feature(def_feature)
        out_feature.SetGeometry(buffer)
        out_lyr.CreateFeature(out_feature)
        out_feature = None
    out_ds.FlushCache()
    del in_ds, out_ds


def smoothing(inShp, fname, bdistance=0.001):
    """
    :param inShp: the path of input shapefile
    :param fname: the path of output shapefile
    :param bdistance: the distance of buffer
    :return:
    """
    ogr.UseExceptions()
    in_ds = ogr.Open(inShp)
    in_lyr = in_ds.GetLayer()
    # 创建输出Buffer文件
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if Path(fname).exists():
        driver.DeleteDataSource(fname)
    # 新建DataSource，Layer
    out_ds = driver.CreateDataSource(fname)
    out_lyr = out_ds.CreateLayer(fname, in_lyr.GetSpatialRef(), ogr.wkbPolygon)
    def_feature = out_lyr.GetLayerDefn()
    # 遍历原始的Shapefile文件给每个Geometry做Buffer操作
    for feature in in_lyr:
        geometry = feature.GetGeometryRef()
        buffer = geometry.Buffer(bdistance).Buffer(-bdistance)
        out_feature = ogr.Feature(def_feature)
        out_feature.SetGeometry(buffer)
        out_lyr.CreateFeature(out_feature)
        out_feature = None
    out_ds.FlushCache()
    del in_ds, out_ds


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
