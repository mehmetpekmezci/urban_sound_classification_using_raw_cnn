#!/usr/bin/env python3
from USCHeader import *
from USCLogger import *
from USCData import *
from USCModel import *
from USCAutoEncoder import *


def main(_):
 continue_training=""
 if len(sys.argv) > 1 :
     continue_training=sys.argv[1]
 uscLogger=USCLogger()
 uscData=USCData(uscLogger.logger)
 uscData.findListOfYoutubeDataFiles()
  
 config = tf.ConfigProto()
 config.gpu_options.allow_growth = True

 with tf.Session(config=config) as session:
   session.run(tf.global_variables_initializer())
   
   uscAutoEncoder=USCAutoEncoder(session,uscLogger,uscData)
   if uscAutoEncoder.alreadyTrained and continue_training!="contiune_training":
        uscLogger.logger.info("AutoEncoder is already trained by-passing this phase ... ")
   else:
    #youtube data also contains urban sound data , replicated 10 times
    for trainingIterationNo in range(uscData.youtube_data_max_category_data_file_count*10):
    #for trainingIterationNo in range(uscData.youtube_data_max_category_data_file_count):
     uscLogger.logger.info("AutoEncoder Training Iteration No: "+str(trainingIterationNo))
     current_youtube_data_as_list=np.random.permutation(uscData.loadNextYoutubeData())
     uscLogger.logAutoEncoderStepStart(session,trainingIterationNo)
     prepareDataTimes=[ ]
     trainingTimes=[ ]
     trainingLosses=[ ]
     trainingAccuracies=[ ]
     for current_batch_counter in range(math.floor(len(current_youtube_data_as_list)/uscData.mini_batch_size)) :
         batch_data=current_youtube_data_as_list[current_batch_counter*uscData.mini_batch_size:(current_batch_counter+1)*uscData.mini_batch_size]
         #uscLogger.logger.info("batch_data.shape: "+str(batch_data.shape))
         trainingTime,trainingLoss,accuracy,prepareDataTime=uscAutoEncoder.train(batch_data)
         trainingTimes.append(trainingTime)
         trainingLosses.append(trainingLoss)
         prepareDataTimes.append(prepareDataTime)
         trainingAccuracies.append(accuracy)
     uscLogger.logAutoEncoderStepEnd(session,prepareDataTimes,trainingTimes,trainingLosses,trainingAccuracies,trainingIterationNo)
  
   ### AUTO ENCODER RAINING FINISHED, STARTING TO TRAIN MODEL

   uscData.prepareData()
   uscModel=USCModel(session,uscLogger,uscData,uscAutoEncoder)
   for trainingIterationNo in range(uscModel.training_iterations):
    uscLogger.logStepStart(session,trainingIterationNo)
    prepareDataTimes=[ ]
    trainingTimes=[ ]
    trainingAccuracies=[ ]
    testTimes=[ ]
    testAccuracies=[ ]
    for fold in np.random.permutation(uscData.fold_dirs):

       if fold == "fold10":
              uscLogger.logger.info("Testing Fold : "+fold)
       else :
           uscLogger.logger.info("Training Fold : "+fold)

       #uscLogger.logger.info("  Fold : "+str(fold))
       current_fold_data=uscData.get_fold_data(fold)
       for current_batch_counter in range(int(current_fold_data.shape[0]/uscData.mini_batch_size)) :
         if (current_batch_counter+1)*uscData.mini_batch_size <= current_fold_data.shape[0] :
           batch_data=current_fold_data[current_batch_counter*uscData.mini_batch_size:(current_batch_counter+1)*uscData.mini_batch_size,:]
         else:
           batch_data=current_fold_data[current_batch_counter*uscData.mini_batch_size:,:]
         if fold == "fold10":
             ## FOLD10 is reserved for testing
              #uscLogger.logger.info("  Testing Batch Counter : "+str(current_batch_counter))
              testTime,testAccuracy=uscModel.test(batch_data)
              testTimes.append(testTime)
              testAccuracies.append(testAccuracy)
         else:
              #uscLogger.logger.info("  Training Batch Counter : "+str(current_batch_counter))
              trainingTime,trainingAccuracy,prepareDataTime=uscModel.train(batch_data)
              trainingTimes.append(trainingTime)
              trainingAccuracies.append(trainingAccuracy)
              prepareDataTimes.append(prepareDataTime)
    uscLogger.logStepEnd(session,prepareDataTimes,trainingTimes,trainingAccuracies,testTimes,testAccuracies,trainingIterationNo)

if __name__ == '__main__':
 tf.app.run(main=main)


