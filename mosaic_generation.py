import ee
try:
    ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
except:
    ee.Authenticate()
    ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')

def getImageCollection(studyArea,startDate,endDate):
  sensorBandDictLandsatTOA = ee.Dictionary({
    L8 : ee.List([1,2,3,4,5,11,6,'BQA']),
    L7 : ee.List([0,1,2,3,4,5,7,'BQA']),
    L5 : ee.List([0,1,2,3,4,5,6,'BQA']),
    L4 : ee.List([0,1,2,3,4,5,6,'BQA'])
  })
  bandNamesLandsatTOA = ee.List(['blue','green','red','nir','swir1','temp','swir2','BQA'])

  l4TOAs = ee.ImageCollection('LANDSAT/LT04/C01/T1_TOA')\
      .filterDate(startDate,endDate)\
      .filterBounds(studyArea)\
      .select(sensorBandDictLandsatTOA.get('L4'),bandNamesLandsatTOA)
    
  l5TOAs = ee.ImageCollection('LANDSAT/LT05/C01/T1_TOA')\
      .filterDate(startDate,endDate)\
      .filterBounds(studyArea)\
      .select(sensorBandDictLandsatTOA.get('L5'),bandNamesLandsatTOA)
  
  l8TOAs = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')\
      .filterDate(startDate,endDate)\
      .filterBounds(studyArea)\
      .select(sensorBandDictLandsatTOA.get('L8'),bandNamesLandsatTOA)


  l7TOAs = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA')\
      .filterDate(startDate,endDate)\
      .filterBounds(studyArea)\
      .select(sensorBandDictLandsatTOA.get('L7'),bandNamesLandsatTOA)
  
  ls = ee.ImageCollection(l5TOAs.merge(l7TOAs).merge(l8TOAs))
  out = ls
  return out


def bqaFunction (image):
  bqa = image.select('BQA');
  if(year > 2013):
    image = image.mask(bqa.eq(2720))
  else:
    image = image.mask(bqa.eq(672))
  return image



def createIndexs(image) :
  MNDWI      = None
  NDVI       = None
  MNDWI_calc = None
  NDVI_calc  = None
  EVI        = None
  EVI_2      = None
  NDWI       = None
  NDWI_GAO_calc = None
  CAI        = None
  PRI        = None
  SAVI       = None
  WVI        = None
  WVI_GAO    = None
  MMDI_v1    = None
  MMDI_v2    = None
  NDSI       = None
   
  # Gerando NDVI
  NDVI = image.expression(
        '(((banda4 - banda3)/(banda4 + banda3)))', {
        'banda4': image.select('nir'),
        'banda3': image.select('red')
  })
  NDSI = image.expression(
        '(((banda5 - banda4)/(banda4 + banda5)))', {
        'banda5': image.select('swir1'),
        'banda4': image.select('nir')
  })

  EVI = image.expression(
        '(2.5 * ( ((banda4 - banda3)) / ((banda4 + (6 * banda3)) - (7.5 * banda1) + 1 ) )) ', {
        'banda1' : image.select('blue'),
        'banda3' : image.select('red'),
        'banda4' : image.select('nir')
  })

  NDWI = image.expression(
        '((banda2 - banda4)/ (banda4 + banda2))', {
        'banda2' : image.select('green'),
        'banda4' : image.select('nir')
  })

  NDWI_GAO_calc = image.expression(
        '((banda4 - banda5)**2 / (banda4 + banda5)**2)**(1/2)', {
        'banda4' : image.select('nir'),
        'banda5' : image.select('swir1')
  })

  MNDWI = image.expression(
        '((( banda2 - banda5) / (banda2 + banda5)))', {
        'banda2': image.select('green'),
        'banda5': image.select('swir1'),
  })

  MNDWI_calc = image.expression(
        '(( banda2 - banda5)**2 / (banda2 + banda5)**2)**(1/2)', {
        'banda2': image.select('green'),
        'banda5': image.select('swir1'),
  })

  NDVI_calc = image.expression(
        '((banda4 - banda3)**2/ (banda4 + banda3)**2)**(1/2)', {
        'banda4': image.select('nir'),
        'banda3': image.select('red'),
        'banda2': image.select('green'),
  })

  #(Simplified Using Modules - Iury Angelo - "(abs(a-b) * abs(c+d) - abs(c-d) * abs(a+b))/(abs(a-b) * abs(c+d) + abs(c-d) * abs(a+b))"
  MMDI_v1 = image.expression(
      '(abs(banda2 - banda5) * abs(banda4 + banda3) - abs(banda4 - banda3) * (banda2 + banda5)) / (abs(banda2 - banda5) * abs(banda4 + banda3) + abs(banda4 - banda3) * abs(banda2 + banda5))', {
        'banda2': image.select('green'),
        'banda3': image.select('red'),
        'banda4': image.select('nir'),
        'banda5': image.select('swir1'),
  })

 
  maskedImage = image\
    .addBands(image.metadata('system:time_start'))\
    .addBands(NDVI.rename('NDVI'))\
    .addBands(NDSI.rename('NDSI'))\
    .addBands(MNDWI.rename('MNDWI'))\
    .addBands(EVI.rename('EVI'))\
    .addBands(NDWI.rename('NDWI'))\
    .addBands(MMDI_v1.rename('MMRI'))\

  return  maskedImage


# Main CODE
geometry = ee.Geometry.Polygon(
        [[[-51.85546875, 5.266007882805497],
          [-52.294921875, 3.337953961416485],
          [-51.317138671875, 0.39550467153201946],
          [-49.52124573640583, -0.6920858950288072],
          [-48.49365234375, -1.4610232806227417],
          [-42.890625, -3.8642546157213955],
          [-39.55078125, -4.740675384778361],
          [-35.9912109375, -6.358975327235661],
          [-36.38671875, -9.44906182688142],
          [-38.49609375, -11.695272733029402],
          [-39.7265625, -13.752724664396975],
          [-39.375, -15.961329081596647],
          [-40.25390625, -18.145851771694467],
          [-40.78125, -19.642587534013032],
          [-42.36328125, -22.105998799750555],
          [-45.52734375, -22.593726063929296],
          [-48.69140625, -24.686952411999144],
          [-49.39453125, -26.431228064506428],
          [-49.74609375, -28.613459424004418],
          [-52.3828125, -31.503629305773018],
          [-54.31640625, -32.99023555965106],
          [-52.91015625, -33.72433966174759],
          [-49.39453125, -30.14512718337612],
          [-48.33984375, -28.76765910569124],
          [-47.28515625, -25.482951175355307],
          [-44.47265625, -23.885837699861995],
          [-42.1875, -23.725011735951796],
          [-40.25390625, -22.593726063929296],
          [-37.6171875, -16.130262012034756],
          [-37.96875, -13.752724664396975],
          [-36.2109375, -12.039320557540572],
          [-34.1015625, -9.102096738726443],
          [-33.92578125, -6.315298538330034],
          [-34.63334381058809, -4.370164795779153],
          [-38.14453125, -3.5134210456400323],
          [-42.01171875, -1.9332268264771106],
          [-45.17578125, -0.8788717828324148],
          [-47.63671875, 0.17578097424708533],
          [-49.921875, 1.9332268264771233],
          [-50.625, 3.8642546157214084]]])

studyArea = geometry
year      = 2021
startDate = year+'-01-01'
endDate   = (year)+'-12-30'

mosaicMerge = getImageCollection(studyArea,startDate,endDate).map(createIndexs).map(bqaFunction)
paleta      = ['008100', '389D2E', '76B956', 'A7D17A','D0E899', 'F8F4BD', 'F0D9CA', 'E2BFD1', 'D2A5D8', 'AC93E2', '7C85EF', '347AF9', '006CFD', '0057E0', '4238BA', '5614BC']

mosaicMerge_tradicional = mosaicMerge.median()
mosaicMerge = mosaicMerge_tradicional.select(['green','red','nir','swir1','swir2']).multiply(255)
mosaicMerge = mosaicMerge.addBands(mosaicMerge_tradicional.select(['NDSI','NDVI','MNDWI','NDWI','MMRI']).add(1).multiply(127))

export  = ee.batch.Export.image.toAsset(
    image       = mosaicMerge.select(['red','nir','swir1','swir2','NDVI','NDWI','NDSI']).set({'year':year,'mosaic':1,'version':5,'collection':3}).toByte(),
    description = 'mosaico_zc_'+year,
    assetId     = '__PATH__'+year,
    region      = geometry,
    scale       = 30,
    maxPixels   = 1e13,
)
# export.start()