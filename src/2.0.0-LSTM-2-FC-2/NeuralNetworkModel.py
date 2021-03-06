#!/usr/bin/env python3
from header import *
from data import *


##
## NueralNetworkModel will be as :
## CNN LAYERS + LSTM LAYERS + FULLY CONNECTED LAYER + SOFTMAX
##
class NeuralNetworkModel :
 def __init__(self, session, logger, input_size=INPUT_SIZE, output_size=OUTPUT_SIZE , keep_prob=DROP_OUT
             , learning_rate=LEARNING_RATE, mini_batch_size=MINI_BATCH_SIZE, time_slice_length=TIME_SLICE_LENGTH,time_slice_overlap_length=TIME_SLICE_OVERLAP_LENGTH, 
               fully_connected_layers=FULLY_CONNECTED_LAYERS,
               learning_rate_beta1=LEARNING_RATE_BETA1, 
               learning_rate_beta2=LEARNING_RATE_BETA2, 
               epsilon=EPSILON,keep_prob_constant=KEEP_PROB,
               number_of_lstm_layers=NUMBER_OF_LSTM_LAYERS, lstm_state_size=LSTM_STATE_SIZE,lstm_forget_bias=LSTM_FORGET_BIAS):
   self.session               = session
   self.logger                = logger
   self.input_size            = input_size
   self.output_size           = output_size
   self.learning_rate         = learning_rate 
   self.mini_batch_size       = mini_batch_size
   self.time_slice_length     = time_slice_length
   self.time_slice_overlap_length= time_slice_overlap_length
   self.number_of_lstm_layers = number_of_lstm_layers
   self.lstm_state_size       = lstm_state_size
   self.lstm_forget_bias      = lstm_forget_bias
   self.fully_connected_layers= fully_connected_layers
   self.keep_prob             = keep_prob
   self.keep_prob_constant    = keep_prob
   self.learning_rate_beta1   = learning_rate_beta1
   self.learning_rate_beta2   = learning_rate_beta2
   self.epsilon               = epsilon

   
   
   ##
   ## DEFINE PLACE HOLDER FOR REAL OUTPUT VALUES FOR TRAINING
   ##
   self.real_y_values=tf.placeholder(tf.float32, shape=(self.mini_batch_size, self.output_size), name="real_y_values")
   self.keep_prob=tf.placeholder(tf.float32, name="keep_prob")

   ##
   ## BUILD THE NETWORK
   ##

   ##
   ## INPUT  LAYER
   ##
   self.x_input = tf.placeholder(tf.float32, shape=(self.mini_batch_size, self.input_size), name="input")
   # x_input.shape[1]=time_slice_length+ number_of_time_slices * (time_slice_length-time_slice_overlap_length) 
   a=self.x_input.shape[1]-self.time_slice_length
   b=self.time_slice_length-self.time_slice_overlap_length
   self.number_of_time_slices=int(a)/int(b)+1
   
   
   with tf.name_scope('input_overlapped_reshape'):
    logger.info("self.x_input.shape="+str(self.x_input.shape))
    #self.x_input_reshaped = tf.reshape(self.x_input, [self.mini_batch_size, self.number_of_time_slices, int(self.input_size/self.number_of_time_slices)])

    # You can use tf.nn.conv2d to help. Basically, you take a sliding filter of block_size over the input, 
    # stepping by stride. To make all the matrix indexes line up, you have to do some reshaping.    
    #def overlap(tensor, block_size=3, stride=2):
    stride=time_slice_length-time_slice_overlap_length
    reshaped = tf.reshape(self.x_input, [self.mini_batch_size,1,-1,1])
    
    ones = tf.ones(time_slice_length, dtype=tf.float32)
    ident = tf.diag(ones)
    filter_dim = [1, time_slice_length, time_slice_length, 1]
    filter_matrix = tf.reshape(ident, filter_dim)
    stride_window = [1, 1, stride, 1]
    filtered_conv = []
    for f in tf.unstack(filter_matrix, axis=1):
      reshaped_filter = tf.reshape(f, [1, time_slice_length, 1, 1])
      c = tf.nn.conv2d(reshaped, reshaped_filter, stride_window, padding='VALID')
      filtered_conv.append(c)
    t = tf.stack(filtered_conv, axis=3)
    self.x_input_reshaped = tf.squeeze(t)
    #def overlapping_blocker(tensor,block_size=3,stride=2):   
    #self.x_input_reshaped = tf.reshape(self.x_input, [self.mini_batch_size, self.number_of_time_slices, int(self.input_size/self.number_of_time_slices)])
    # Unstack to get a list of 'number_of_time_slices' tensors of shape (batch_size, input_size/number_of_time_slices,number_of_input_channels)

    logger.info("self.number_of_time_slices="+str(self.number_of_time_slices))
    self.x_input_list = tf.unstack(self.x_input_reshaped, self.number_of_time_slices, 1)
    logger.info("self.x_input[0].shape"+str(self.x_input_list[0].shape))
   
   ##
   ## LSTM LAYERS
   ##
   with tf.name_scope("lstm"):
    ####lstm_cell = tf.nn.rnn_cell.LSTMCell(self.lstm_state_size)
    lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.lstm_state_size, forget_bias=self.lstm_forget_bias)
    # create a RNN cell composed sequentially of a number of RNNCells
    ####multi_lstm_cell = tf.nn.rnn_cell.MultiRNNCell([lstm_cell] * self.number_of_lstm_layers)
    # 'outputs' is a tensor of shape [batch_size, max_time, 256]
    # 'state' is a N-tuple where N is the number of LSTMCells containing a tf.contrib.rnn.LSTMStateTuple for each cell : 
    #    tf.nn.rnn_cell.LSTMStateTuple(lstm_cell_state , lstm_hidden_state) 
    lstm_cell_with_dropout=tf.nn.rnn_cell.DropoutWrapper(lstm_cell, output_keep_prob=self.keep_prob)
    #lstm_cell_with_dropout=tf.nn.rnn.DropoutWrapper(lstm_cell, output_keep_prob=self.keep_prob_)
    lstm_outputs, lstm_state = tf.nn.static_rnn(lstm_cell_with_dropout, inputs=self.x_input_list, dtype=tf.float32)
    self.logger.info("lstm_outputs="+str( lstm_outputs))
    self.logger.info("lstm_state="+str( lstm_state))
    
    last_layer_output=lstm_outputs[-1]
    
    # Linear activation, using rnn inner loop last output
    
    #weights = {'out': tf.Variable(tf.random_normal([self.lstm_state_size, self.output_size ]))}
    #biases = {'out': tf.Variable(tf.random_normal([self.output_size ]))}
    #self.y_outputs=tf.matmul(lstm_outputs[-1], weights['out']) + biases['out']
    ## get last element of lstm_outputs = lstm_outputs[-1]= output for the last time step = final output = generated (guess) value  .
   



   for fcLayerNo in range(len(self.fully_connected_layers)) :
       
    number_of_fully_connected_layer_neurons=self.fully_connected_layers[fcLayerNo]

    with tf.name_scope('fc-'+str(fcLayerNo)):
     W_fc1 =  tf.Variable( tf.truncated_normal([int(last_layer_output.shape[1]), number_of_fully_connected_layer_neurons], stddev=0.1))
     self.logger.info("W_fc-"+str(fcLayerNo)+".shape="+str(W_fc1.shape))
     B_fc1 = tf.Variable(tf.constant(0.1, shape=[number_of_fully_connected_layer_neurons]))
     self.logger.info("B_fc-"+str(fcLayerNo)+".shape="+str(B_fc1.shape))
     matmul_fc1=tf.matmul(last_layer_output, W_fc1)+B_fc1
     self.logger.info("matmul_fc-"+str(fcLayerNo)+".shape="+str(matmul_fc1.shape))

    with tf.name_scope('fc-'+str(fcLayerNo)+'_batch_normlalization'):    
     batch_mean, batch_var = tf.nn.moments(matmul_fc1,[0])
     scale = tf.Variable(tf.ones(number_of_fully_connected_layer_neurons))
     beta = tf.Variable(tf.zeros(number_of_fully_connected_layer_neurons))
     batch_normalization_fc1 = tf.nn.batch_normalization(matmul_fc1,batch_mean,batch_var,beta,scale,epsilon)
     self.logger.info("batch_normalization_fc-"+str(fcLayerNo)+".shape="+str(batch_normalization_fc1.shape))

    with tf.name_scope('fc-'+str(fcLayerNo)+'_batch_normalized_relu'):    
     h_fc1 = tf.nn.relu( batch_normalization_fc1 )
     self.logger.info("h_fc-"+str(fcLayerNo)+".shape="+str(h_fc1.shape))

    # Dropout - controls the complexity of the model, prevents co-adaptation of features.
    with tf.name_scope('fc-'+str(fcLayerNo)+'_dropout'):    
     h_fc1_drop = tf.nn.dropout(h_fc1, self.keep_prob)
     self.logger.info("h_fc-"+str(fcLayerNo)+"_drop.shape="+str(h_fc1_drop.shape))
     last_layer_output=h_fc1_drop


   # Map the NUMBER_OF_FULLY_CONNECTED_NEURONS features to OUTPUT_SIZE=NUMBER_OF_CLASSES(10) classes, one for each class
   with tf.name_scope('last_fc'):
    W_fc2 =  tf.Variable( tf.truncated_normal([number_of_fully_connected_layer_neurons, self.output_size], stddev=0.1))
    b_fc2 =  tf.Variable(tf.constant(0.1, shape=[self.output_size]))
    #h_fc2 =tf.nn.relu( tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
    self.y_outputs =tf.matmul(last_layer_output, W_fc2) + b_fc2
    self.logger.info("self.y_outputs.shape="+str(self.y_outputs.shape))


    ## HERE NETWORK DEFINITION IS FINISHED
    
    ###  NOW CALCULATE PREDICTED VALUE
    #with tf.name_scope('calculate_predictions'):
    # output_shape = tf.shape(self.y_outputs)
    # self.predictions = tf.nn.softmax(tf.reshape(self.y_outputs, [-1, self.output_size]))
     
   ##
   ## CALCULATE LOSS
   ##
    with tf.name_scope('calculate_loss'):
     cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=self.real_y_values,logits=self.y_outputs)
     self.loss = tf.reduce_mean(cross_entropy)

   ##
   ## SET OPTIMIZER
   ##
   with tf.name_scope('optimizer'):
    self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate,beta1=0.9,beta2=0.99).minimize(self.loss)

   ##
   ## CALCULATE ACCURACY
   ##
   with tf.name_scope('calculate_accuracy'):
    correct_prediction = tf.equal(tf.argmax(self.y_outputs, 1),tf.argmax(self.real_y_values, 1))
    correct_prediction = tf.cast(correct_prediction, tf.float32)
    self.accuracy = tf.reduce_mean(correct_prediction)


   ##
   ## SAVE NETWORK GRAPH TO A DIRECTORY
   ##
   with tf.name_scope('save_graph'):
    self.logger.info('Saving graph to: %s' % LOG_DIR_FOR_TF_SUMMARY)
    graph_writer = tf.summary.FileWriter(LOG_DIR_FOR_TF_SUMMARY)
    graph_writer.add_graph(tf.get_default_graph())
   
   

   ##
   ## INITIALIZE SESSION
   ##
   #checkpoint= tf.train.get_checkpoint_state(os.path.dirname(SAVE_DIR+'/usc_model'))
   #if checkpoint and checkpoint.model_checkpoint_path:
  #  saver.restore(self.session,checkpoint.model_checkpoint_path)
  # else : 
  #  self.session.run(tf.global_variables_initializer())

 def prepareData(self,data,augment):
  x_data=data[:,:4*SOUND_RECORD_SAMPLING_RATE]
  if augment==True :
    x_data=augment_random(x_data)
  y_data=data[:,4*SOUND_RECORD_SAMPLING_RATE]
  y_data_one_hot_encoded=one_hot_encode_array(y_data)
  return x_data,y_data_one_hot_encoded

 def train(self,data):
  augment=True
  prepareDataTimeStart = int(round(time.time())) 
  x_data,y_data=self.prepareData(data,augment)
  prepareDataTimeStop = int(round(time.time())) 
  prepareDataTime=prepareDataTimeStop-prepareDataTimeStart
  trainingTimeStart = int(round(time.time())) 
  #self.logger.info('self.session.run(self.x_input_list[0][0][self.time_slice_length-self.time_slice_overlap_length],feed_dict={self.x_input: x_data})=')
  #self.logger.info(self.session.run(self.x_input_list[0][0][self.time_slice_length-self.time_slice_overlap_length],feed_dict={self.x_input: x_data}))
  #self.logger.info('self.session.run(self.x_input_list[1][0][0],feed_dict={self.x_input: x_data})=')
  #self.logger.info(self.session.run(self.x_input_list[1][0][0],feed_dict={self.x_input: x_data}))
  self.optimizer.run(feed_dict={self.x_input: x_data, self.real_y_values:y_data, self.keep_prob:self.keep_prob_constant})

  trainingTimeStop = int(round(time.time())) 
  trainingTime=trainingTimeStop-trainingTimeStart
  trainingAccuracy = self.accuracy.eval(feed_dict={self.x_input: x_data, self.real_y_values:y_data, self.keep_prob: 1.0})
  return trainingTime,trainingAccuracy,prepareDataTime
     
 def test(self,data):
  testTimeStart = int(round(time.time())) 
  augment=False
  x_data,y_data=self.prepareData(data,augment) 
  testAccuracy = self.accuracy.eval(feed_dict={self.x_input: x_data, self.real_y_values:y_data, self.keep_prob: 1.0})
  testTimeStop = int(round(time.time())) 
  testTime=testTimeStop-testTimeStart
  return testTime,testAccuracy
  



