#!/usr/bin/env python3
from header import *

def parse_audio_files():

    global RAW_DATA_DIR,CSV_DATA_DIR,FOLD_DIRS
    sub4SecondSoundFilesCount=0
    for sub_dir in FOLD_DIRS:
      logger.info("Parsing : "+sub_dir)
      csvDataFile=open(CSV_DATA_DIR+"/"+sub_dir+".csv", 'w')
      csvDataWriter = csv.writer(csvDataFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
      for file_path in glob.glob(os.path.join(RAW_DATA_DIR, sub_dir, '*.wav')):
         logger.info(file_path)
         try :
          classNumber=file_path.split('/')[-1].split('.')[0].split('-')[1]
          sound_data,sampling_rate=librosa.load(file_path)
          sound_data=np.array(sound_data)
          sound_data_duration=int(sound_data.shape[0]/SOUND_RECORD_SAMPLING_RATE)
          if sound_data_duration < 4 :
             sub4SecondSoundFilesCount=sub4SecondSoundFilesCount+1
             sound_data_in_4_second=np.zeros(4*SOUND_RECORD_SAMPLING_RATE)
             for i in range(sound_data.shape[0]):
               sound_data_in_4_second[i]=sound_data[i]
          else  :  
             sound_data_in_4_second=sound_data[:4*SOUND_RECORD_SAMPLING_RATE]
          sound_data_in_4_second=np.append(sound_data_in_4_second,[classNumber])
          csvDataWriter.writerow(sound_data_in_4_second)       
         except :
                e = sys.exc_info()[0]
                logger.info ("Exception :")
                logger.info (e)
      csvDataFile.close()       
      logger.info("sub4SecondSoundFilesCount="+str(sub4SecondSoundFilesCount));  


def prepareData():
    logger.info("Starting to prepare the data ...  ")

    global RAW_DATA_DIR,CSV_DATA_DIR,FOLD_DIRS
    logger.info ("prepareData function ...")
    if not  os.path.exists(RAW_DATA_DIR) :
       if not  os.path.exists(MAIN_DATA_DIR+'/../data/0.raw'):
         os.makedirs(MAIN_DATA_DIR+'/../data/0.raw')   
    if not os.path.exists(MAIN_DATA_DIR+"/0.raw/UrbanSound8K"):
      if os.path.exists(MAIN_DATA_DIR+"/0.raw/UrbanSound8K.tar.gz"):
         logger.info("Extracting "+MAIN_DATA_DIR+"/0.raw/UrbanSound8K.tar.gz")
         tar = tarfile.open(MAIN_DATA_DIR+"/0.raw/UrbanSound8K.tar.gz")
         tar.extractall(MAIN_DATA_DIR+'/../data/0.raw')
         tar.close()
         logger.info("Extracted "+MAIN_DATA_DIR+"/0.raw/UrbanSound8K.tar.gz")
      else :   
         logger.info("download "+MAIN_DATA_DIR+"/0.raw/UrbanSound8K.tar.gz from http://serv.cusp.nyu.edu/files/jsalamon/datasets/content_loader.php?id=2  using firefox browser or chromium  and re-run this script")
         # logger.info("download "+MAIN_DATA_DIR+"/0.raw/UrbanSound8K.tar.gz from https://serv.cusp.nyu.edu/projects/urbansounddataset/download-urbansound8k.html using firefox browser or chromium  and re-run this script")
         exit(1)
#         http = urllib3.PoolManager()
#         chunk_size=100000
#         r = http.request('GET', 'http://serv.cusp.nyu.edu/files/jsalamon/datasets/content_loader.php?id=2', preload_content=False)
#         with open(MAIN_DATA_DIR+"/0.raw/UrbanSound8K.tar.gz", 'wb') as out:
#          while True:
#           data = r.read(chunk_size)
#           if not data:
#             break
#           out.write(data)
#         r.release_conn()

    if not os.path.exists(CSV_DATA_DIR) :
       os.makedirs(CSV_DATA_DIR)  
       parse_audio_files()
    logger.info("Data is READY  in CSV format. ")
    
def normalize(data):
    global MAX_VALUE_FOR_NORMALIZATION , MIN_VALUE_FOR_NORMALIZATION
    data_normalized=(data-MIN_VALUE_FOR_NORMALIZATION)/(MAX_VALUE_FOR_NORMALIZATION-MIN_VALUE_FOR_NORMALIZATION)
    return data_normalized

def one_hot_encode_array(arrayOfYData):
   returnMatrix=np.empty([0,NUMBER_OF_CLASSES]);
   for i in range(arrayOfYData.shape[0]):
        one_hot_encoded_class_number = np.zeros(NUMBER_OF_CLASSES)
        one_hot_encoded_class_number[int(arrayOfYData[i])]=1
        returnMatrix=np.row_stack([returnMatrix, one_hot_encoded_class_number])
   return returnMatrix

def one_hot_encode(classNumber):
   one_hot_encoded_class_number = np.zeros(NUMBER_OF_CLASSES)
   one_hot_encoded_class_number[int(classNumber)]=1
   return one_hot_encoded_class_number

def load_all_csv_data_back_to_memory():
     logger.info ("load_all_csv_data_back_to_memory function started ...")
     global fold_data_dictionary, MAX_VALUE_FOR_NORMALIZATION ,  MIN_VALUE_FOR_NORMALIZATION
     for fold in FOLD_DIRS:
       fold_data_dictionary[fold]=np.array(np.loadtxt(open(CSV_DATA_DIR+"/"+fold+".csv", "rb"), delimiter=","))
       for i in range(fold_data_dictionary[fold].shape[0]) :
          loadedData=fold_data_dictionary[fold][i]
          loadedDataX=loadedData[:4*SOUND_RECORD_SAMPLING_RATE]
          loadedDataY=loadedData[4*SOUND_RECORD_SAMPLING_RATE]
          maxOfArray=np.amax(loadedDataX)
          minOfArray=np.amin(loadedDataX)
          if MAX_VALUE_FOR_NORMALIZATION < maxOfArray :
              MAX_VALUE_FOR_NORMALIZATION = maxOfArray
          if MIN_VALUE_FOR_NORMALIZATION > minOfArray :
              MIN_VALUE_FOR_NORMALIZATION = minOfArray
          ## Then append Y data to the end of row
          fold_data_dictionary[fold][i]=np.append(loadedDataX,loadedDataY)
     
     logger.info ("load_all_csv_data_back_to_memory function finished ...")

def normalize_all_data():
     logger.info ("normalize_all_data function started ...")
     global fold_data_dictionary
     for fold in FOLD_DIRS:
       for i in range(fold_data_dictionary[fold].shape[0]) :
          loadedData=fold_data_dictionary[fold][i]
          loadedDataX=loadedData[:4*SOUND_RECORD_SAMPLING_RATE]
          loadedDataY=loadedData[4*SOUND_RECORD_SAMPLING_RATE]
          normalizedLoadedDataX=normalize(loadedDataX)
          fold_data_dictionary[fold][i]=np.append(normalizedLoadedDataX,loadedDataY)
     logger.info ("normalize_all_data function finished ...")

def get_fold_data(fold):
     global fold_data_dictionary
     return np.random.permutation(fold_data_dictionary[fold])


def slice_data(data,number_of_time_slices) :
   return np.reshape(data,[-1,number_of_time_slices,int(data.shape[1]/number_of_time_slices)])
  

def augment_speedx(sound_array, factor):
    """ Multiplies the sound's speed by some `factor` """
    result=np.zeros(len(sound_array))
    indices = np.round( np.arange(0, len(sound_array), factor) )
    indices = indices[indices < len(sound_array)].astype(int)
    result_calculated= sound_array[ indices.astype(int) ]
    if len(result) > len(result_calculated) :
       result[:len(result_calculated)]=result_calculated
    else :
        result=result_calculated[:len(result)]
    return result

def augment_inverse(sound_array):
    return -sound_array

def augment_volume(sound_array,factor):
    return factor * sound_array

def augment_translate(snd_array, n):
    """ Translates the sound wave by n indices, fill the first n elements of the array with zeros """
    new_array=np.zeros(len(snd_array))
    for i in range(snd_array.shape[0]):
       if i+n == len(new_array) :
          break
       new_array[i+n]=snd_array[i] 
    return new_array


def augment_random(x_data):
  augmented_data= np.zeros([x_data.shape[0],x_data.shape[1]],np.float32)
  for i in range(x_data.shape[0]) :
    augmented_data[i]=x_data[i]
    IS_AUGMENT_DATA=random.randint(0, 9)
    # 10 percent of being not augmented , if equals 0, then not augment, return directly real value
    # 10 percent of being random noise
    # 80 percent of being  augmented
    if IS_AUGMENT_DATA > 1 :
      SPEED_FACTOR=random.uniform(0.7,1.3)
      TRANSLATION_FACTOR=random.randint(2000,10000)
      #VOLUME_FACTOR=random.uniform(0.5,2)
      INVERSE_FACTOR=random.randint(0, 1)
      if INVERSE_FACTOR == 1 :
       augmented_data[i]=-augmented_data[i]
      augmented_data[i]=augment_speedx(augmented_data[i],SPEED_FACTOR)
      augmented_data[i]=augment_translate(augmented_data[i],TRANSLATION_FACTOR)
      #augmented_data[i]=augment_volume(augmented_data[i],VOLUME_FACTOR)
    if IS_AUGMENT_DATA == 1 :
      augmented_data= np.random.rand(x_data.shape[0],x_data.shape[1])

  return augmented_data
 
