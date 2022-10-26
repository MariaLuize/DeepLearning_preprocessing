from rois import *

import ee
try:
    ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
except:
    ee.Authenticate()
    ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')

year       = 2020
classID    = 32 # hypersaline salt flats (a.k.a. apicum) land cover
class_name = 'apicum'
mosaic_image = ee.Image('Mosaic_PATH_'+ year)
mp62020      = ee.Image('Mapbiomas_past_classification_PATH'+year).eq(classID).toByte()

supervised_class = mp62020.toByte().paint(apicumAdd,1).paint(apicumRemoval,0)

# Training and testing dataset exportation
version = 1
export  = ee.batch.Export.table.toAsset(
    collection  = trainingPolys,
    description = 'trainPoly_unet_'+class_name+'_'+year,
    assetId     = '__PATH__'
)

export  = ee.batch.Export.table.toAsset(
    collection  = testingPools,
    description = 'testPoly_unet_'+class_name+'_'+year,
    assetId     = '__PATH__'
)

export  = ee.batch.Export.image.toAsset(
    image       = supervised_class.select("classification").set({'year':year, 'version':version}),
    description = 'supervisedImage_unet_'+class_name+'_'+year+'_v'+version,
    assetId     = '__PATH__'+year,
    region      = ROI,
    scale       = 30,
    maxPixels   = 1e13,
    shardSize   = 256
)
# export.start()