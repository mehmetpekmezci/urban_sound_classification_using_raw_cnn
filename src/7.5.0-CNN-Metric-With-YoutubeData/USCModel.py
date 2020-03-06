#!/usr/bin/env python3
from USCHeader import *
from USCLogger import *
from USCData import *

##
## NueralNetworkModel will be as :
## CNN LAYERS + LSTM LAYERS + FULLY CONNECTED LAYER + SOFTMAX
##
class USCModel :
 def __init__(self, session, uscLogger,uscData): 
   self.session               = session
   self.uscLogger             = uscLogger
   self.uscData               = uscData
   ## self.uscData.time_slice_length = 440

   script_dir=os.path.dirname(os.path.realpath(__file__))
   script_name=os.path.basename(script_dir)
   self.model_save_dir=script_dir+"/../../save/"+script_name
   self.model_save_file="model.h5"

   ## so we will have nearly 400 time steps in 4 secs record. (88200) (with %50 overlapping)
   self.lstm_time_steps       = self.uscData.number_of_time_slices
   self.training_iterations   = 10000
   self.buildModel()

   self.load_weights()
   self.trainCount=0

   self.model.summary()



 #def cutIntoLSTMSTepSizes(self,inputList):
 #  listOfList=[]
 #  for c in range(int(self.number_of_time_slices/self.number_of_lstm_time_steps)) :
 #     chunk=inputList[c:c*self.number_of_lstm_time_steps]
 #     listOfList.append(chunk)
 #  return listOfList

 def load_weights(self):
     if os.path.exists(self.model_save_dir+"/"+self.model_save_file):
         self.model.load_weights(self.model_save_dir+"/"+self.model_save_file)

 def save_weights(self):
     if not os.path.exists(self.model_save_dir):
         os.makedirs(self.model_save_dir)
     self.model.save_weights(self.model_save_dir+"/"+self.model_save_file)


 def prepareData(self,data,augment):
  x_data=data[:,:4*self.uscData.sound_record_sampling_rate]
  if augment==True :
    x_data=self.uscData.augment_random(x_data)
  x_data=self.uscData.normalize(x_data)
  y_data=data[:,4*self.uscData.sound_record_sampling_rate]
  y_data_one_hot_encoded=self.uscData.one_hot_encode_array(y_data)
  return encodedValue,y_data_one_hot_encoded


 def train(self,data):
  augment=True
  prepareDataTimeStart = int(round(time.time())) 
  x_data,y_data=self.prepareData(data,augment)
  prepareDataTimeStop = int(round(time.time())) 
  prepareDataTime=prepareDataTimeStop-prepareDataTimeStart
  trainingTimeStart = int(round(time.time())) 

  self.model.fit(x_data, y_data, epochs = 1, batch_size = self.uscData.mini_batch_size,verbose=0)
  trainingTimeStop = int(round(time.time())) 
  trainingTime=trainingTimeStop-trainingTimeStart
  evaluation = self.model.evaluate(x_data, y_data, batch_size = self.uscData.mini_batch_size,verbose=0)
  trainingAccuracy = evaluation[1]
  #print(self.model.metrics_names) 
  #print(evaluation) 
  self.trainCount+=1
  if self.trainCount % 100 == 0 :
     self.save_weights()

  return trainingTime,trainingAccuracy,prepareDataTime
     
 def test(self,data):
  testTimeStart = int(round(time.time())) 
  augment=False
  x_data,y_data=self.prepareData(data,augment) 
  evaluation = self.model.evaluate(x_data, y_data,batch_size = self.uscData.mini_batch_size,verbose=0)
  testAccuracy = evaluation[1]
  testTimeStop = int(round(time.time())) 
  testTime=testTimeStop-testTimeStart
  return testTime,testAccuracy
  
# def buildModel(self):
#   layer_input = keras.layers.Input(batch_shape=(self.uscData.mini_batch_size,self.uscData.number_of_time_slices,self.uscData.latent_space_presentation_data_length))
#   out=keras.layers.LSTM(self.lstm_size,dropout=0.2,recurrent_dropout=0.2)(layer_input)
#   out=keras.layers.BatchNormalization()(out)
#   out=keras.layers.Dense(units = 2048,activation='relu')(out)
#   out=keras.layers.BatchNormalization()(out)
#   out=keras.layers.Dropout(0.2)(out)
#   out=keras.layers.Dense(units = 2048,activation='relu')(out)
#   out=keras.layers.BatchNormalization()(out)
#   out=keras.layers.Dropout(0.2)(out)
#   out=keras.layers.Dense(units = self.uscData.number_of_classes,activation='softmax')(out)
#   self.model = keras.models.Model(inputs=[layer_input], outputs=[out])
#   selectedOptimizer=keras.optimizers.Adam(lr=0.0001)
#   self.model.compile(optimizer=selectedOptimizer, loss='categorical_crossentropy',metrics=['accuracy'])



 def buildModel(self):
   layer_input = keras.layers.Input(batch_shape=(self.uscData.mini_batch_size,self.uscData.track_length,2))
   # Convolution1D(filters, kernel_size,...)
   out=keras.layers.Convolution1D(16,64,strides=16,activation='relu', border_mode='same')(layer_input)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Convolution1D(32,32,strides=16,activation='relu', border_mode='same')(layer_input)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Convolution1D(64,16,strides=16,activation='relu', border_mode='same')(layer_input)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Convolution1D(64, 8,strides=2,activation='relu', border_mode='same')(layer_input)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Convolution1D(64, 4,strides=2,activation='relu', border_mode='same')(out)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Convolution1D(64, 4,strides=2,activation='relu', border_mode='same')(out)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Convolution1D(64, 4,activation='relu', border_mode='same')(out)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Convolution1D(64, 4,activation='relu', border_mode='same')(out)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Convolution1D(64, 4,activation='relu', border_mode='same')(out)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Flatten()(out)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Dense(units = 128,activation='sigmoid')(out)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Dense(units = 128,activation='sigmoid')(out)
   out=keras.layers.BatchNormalization()(out)
   out=keras.layers.Dense(units = self.uscData.number_of_classes,activation='softmax')(out)
   self.model = keras.models.Model(inputs=[layer_input], outputs=[out])
   selectedOptimizer=keras.optimizers.Adam(lr=0.0001)
   self.model.compile(optimizer=selectedOptimizer, loss='categorical_crossentropy',metrics=['accuracy'])


