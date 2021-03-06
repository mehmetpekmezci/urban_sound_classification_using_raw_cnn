#!/usr/bin/env python3
from header import *
from data import *


##
## NueralNetworkModel will be as :
## CNN LAYERS + LSTM LAYERS + FULLY CONNECTED LAYER + SOFTMAX
##
class AutoEncoder :
 def __init__(self,session,logger,input_size=INPUT_SIZE,learning_rate=LEARNING_RATE,mini_batch_size=int(MINI_BATCH_SIZE+MINI_BATCH_SIZE_FOR_GENERATED_DATA),encoder_layers=ENCODER_LAYERS,keep_prob_constant=KEEP_PROB,epsilon=EPSILON):

   ##
   ## SET CLASS ATTRIBUTES WITH THE GIVEN INPUTS
   ##
   self.session               = session
   self.logger                = logger
   self.input_size            = input_size
   self.learning_rate         = learning_rate 
   self.mini_batch_size       = mini_batch_size
   self.encoder_layers        = encoder_layers
   self.keep_prob_constant    = keep_prob_constant
   self.epsilon               = epsilon  
  
   self.keep_prob = tf.placeholder(tf.float32)

   ##
   ## BUILD THE NETWORK
   ##

   ##
   ## INPUT  LAYER
   ##
   self.x_input                      = tf.placeholder(tf.float32, shape=(self.mini_batch_size, self.input_size), name="input")
   
   last_layer_output=self.x_input
   with tf.name_scope('encoder'):
    for fcLayerNo in range(len(self.encoder_layers)) :
       number_of_fully_connected_layer_neurons=self.encoder_layers[fcLayerNo]
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
   self.encoder=last_layer_output
   
   
   ### DECODER
   with tf.name_scope('decoder'):
    for fcLayerNo in range(len(self.encoder_layers)) :
       number_of_fully_connected_layer_neurons=self.encoder_layers[int(-1*(fcLayerNo+1))]
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

   ### OUTPUT
   with tf.name_scope('output_decoder'):
     W_fc2 =  tf.Variable( tf.truncated_normal([int(last_layer_output.shape[1]), self.input_size], stddev=0.1))
     b_fc2 =  tf.Variable(tf.constant(0.1, shape=[self.input_size]))
     self.y_output =tf.matmul(last_layer_output, W_fc2) + b_fc2
     self.logger.info("self.y_output.shape="+str(self.y_output.shape))
      
    ## HERE NETWORK DEFINITION IS FINISHED
     
   ##
   ## CALCULATE LOSS
   ##
   with tf.name_scope('calculate_loss'):
     self.loss=tf.losses.mean_squared_error(self.x_input,self.y_output)

   ##
   ## SET OPTIMIZER
   ##
   with tf.name_scope('optimizer'):
    self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.loss)

   ##
   ## SAVE NETWORK GRAPH TO A DIRECTORY
   ##
   with tf.name_scope('save_graph'):
    self.logger.info('Saving graph to: %s-autoencoder' % LOG_DIR_FOR_TF_SUMMARY)
    graph_writer = tf.summary.FileWriter(LOG_DIR_FOR_TF_SUMMARY+"-autoencoder")
    graph_writer.add_graph(tf.get_default_graph())

 def prepareData(self,data,generated_data):
  x_data=augment_random(data[:,:4*SOUND_RECORD_SAMPLING_RATE])
  concat_data=np.concatenate((x_data,generated_data),axis=0)
  x_data=np.random.permutation(concat_data)
  return x_data

 def train(self,data,generated_data):
  prepareDataTimeStart = int(round(time.time())) 
  x_data=self.prepareData(data,generated_data)
  prepareDataTimeStop = int(round(time.time())) 
  prepareDataTime=prepareDataTimeStop-prepareDataTimeStart
  trainingTimeStart = int(round(time.time())) 
  self.optimizer.run(feed_dict={self.x_input: x_data,self.keep_prob: self.keep_prob_constant})
  trainingTimeStop = int(round(time.time())) 
  trainingTime=trainingTimeStop-trainingTimeStart
  trainingLoss = self.loss.eval(feed_dict={self.x_input: x_data,self.keep_prob: 1.0})
  return trainingTime,trainingLoss,prepareDataTime
     
 def encode(self,data):
  encodeTimeStart = int(round(time.time())) 
  x_data=data[:,:4*SOUND_RECORD_SAMPLING_RATE]
  encodedValue = self.encoder.eval(feed_dict={self.x_input: x_data, self.keep_prob: 1.0})
  encodeTimeStop = int(round(time.time())) 
  encodeTime=encodeTimeStop-encodeTimeStart
  return encodedValue,encodeTime
  

'''
---------------------------------------------------------------------------------
An Example

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from tensorflow.contrib.layers import fully_connected

mnist=input_data.read_data_sets("/MNIST_data/",one_hot=True)

tf.reset_default_graph()

num_inputs=784    #28x28 pixels
num_hid1=392
num_hid2=196
num_hid3=num_hid1
num_output=num_inputs
lr=0.01
actf=tf.nn.relu

X=tf.placeholder(tf.float32,shape=[None,num_inputs])
initializer=tf.variance_scaling_initializer()

w1=tf.Variable(initializer([num_inputs,num_hid1]),dtype=tf.float32)
w2=tf.Variable(initializer([num_hid1,num_hid2]),dtype=tf.float32)
w3=tf.Variable(initializer([num_hid2,num_hid3]),dtype=tf.float32)
w4=tf.Variable(initializer([num_hid3,num_output]),dtype=tf.float32)

b1=tf.Variable(tf.zeros(num_hid1))
b2=tf.Variable(tf.zeros(num_hid2))
b3=tf.Variable(tf.zeros(num_hid3))
b4=tf.Variable(tf.zeros(num_output))

hid_layer1=actf(tf.matmul(X,w1)+b1)
hid_layer2=actf(tf.matmul(hid_layer1,w2)+b2)
hid_layer3=actf(tf.matmul(hid_layer2,w3)+b3)
output_layer=actf(tf.matmul(hid_layer3,w4)+b4)

loss=tf.reduce_mean(tf.square(output_layer-X))

optimizer=tf.train.AdamOptimizer(lr)
train=optimizer.minimize(loss)

init=tf.global_variables_initializer()

num_epoch=5
batch_size=150
num_test_images=10

with tf.Session() as sess:
    sess.run(init)
    for epoch in range(num_epoch):
        
        num_batches=mnist.train.num_examples//batch_size
        for iteration in range(num_batches):
            X_batch,y_batch=mnist.train.next_batch(batch_size)
            sess.run(train,feed_dict={X:X_batch})
            
        train_loss=loss.eval(feed_dict={X:X_batch})
        print("epoch {} loss {}".format(epoch,train_loss))
        
        
    results=output_layer.eval(feed_dict={X:mnist.test.images[:num_test_images]})
    
    #Comparing original images with reconstructions
    f,a=plt.subplots(2,10,figsize=(20,4))
    for i in range(num_test_images):
        a[0][i].imshow(np.reshape(mnist.test.images[i],(28,28)))
a[1][i].imshow(np.reshape(results[i],(28,28)))







-------------------------------------------------------------------------------------------------------------
Another Example


from __future__ import division, print_function, absolute_import

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)

# Training Parameters
learning_rate = 0.01
num_steps = 30000
batch_size = 256

display_step = 1000
examples_to_show = 10

# Network Parameters
num_hidden_1 = 256 # 1st layer num features
num_hidden_2 = 128 # 2nd layer num features (the latent dim)
num_input = 784 # MNIST data input (img shape: 28*28)

# tf Graph input (only pictures)
X = tf.placeholder("float", [None, num_input])

weights = {
    'encoder_h1': tf.Variable(tf.random_normal([num_input, num_hidden_1])),
    'encoder_h2': tf.Variable(tf.random_normal([num_hidden_1, num_hidden_2])),
    'decoder_h1': tf.Variable(tf.random_normal([num_hidden_2, num_hidden_1])),
    'decoder_h2': tf.Variable(tf.random_normal([num_hidden_1, num_input])),
}
biases = {
    'encoder_b1': tf.Variable(tf.random_normal([num_hidden_1])),
    'encoder_b2': tf.Variable(tf.random_normal([num_hidden_2])),
    'decoder_b1': tf.Variable(tf.random_normal([num_hidden_1])),
    'decoder_b2': tf.Variable(tf.random_normal([num_input])),
}

# Building the encoder
def encoder(x):
    # Encoder Hidden layer with sigmoid activation #1
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['encoder_h1']),
                                   biases['encoder_b1']))
    # Encoder Hidden layer with sigmoid activation #2
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['encoder_h2']),
                                   biases['encoder_b2']))
    return layer_2


# Building the decoder
def decoder(x):
    # Decoder Hidden layer with sigmoid activation #1
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['decoder_h1']),
                                   biases['decoder_b1']))
    # Decoder Hidden layer with sigmoid activation #2
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['decoder_h2']),
                                   biases['decoder_b2']))
    return layer_2

# Construct model
encoder_op = encoder(X)
decoder_op = decoder(encoder_op)

# Prediction
y_pred = decoder_op
# Targets (Labels) are the input data.
y_true = X

# Define loss and optimizer, minimize the squared error
loss = tf.reduce_mean(tf.pow(y_true - y_pred, 2))
optimizer = tf.train.RMSPropOptimizer(learning_rate).minimize(loss)

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Start Training
# Start a new TF session
with tf.Session() as sess:

    # Run the initializer
    sess.run(init)

    # Training
    for i in range(1, num_steps+1):
        # Prepare Data
        # Get the next batch of MNIST data (only images are needed, not labels)
        batch_x, _ = mnist.train.next_batch(batch_size)

        # Run optimization op (backprop) and cost op (to get loss value)
        _, l = sess.run([optimizer, loss], feed_dict={X: batch_x})
        # Display logs per step
        if i % display_step == 0 or i == 1:
            print('Step %i: Minibatch Loss: %f' % (i, l))

    # Testing
    # Encode and decode images from test set and visualize their reconstruction.
    n = 4
    canvas_orig = np.empty((28 * n, 28 * n))
    canvas_recon = np.empty((28 * n, 28 * n))
    for i in range(n):
        # MNIST test set
        batch_x, _ = mnist.test.next_batch(n)
        # Encode and decode the digit image
        g = sess.run(decoder_op, feed_dict={X: batch_x})

        # Display original images
        for j in range(n):
            # Draw the original digits
            canvas_orig[i * 28:(i + 1) * 28, j * 28:(j + 1) * 28] = \
                batch_x[j].reshape([28, 28])
        # Display reconstructed images
        for j in range(n):
            # Draw the reconstructed digits
            canvas_recon[i * 28:(i + 1) * 28, j * 28:(j + 1) * 28] = \
                g[j].reshape([28, 28])

    print("Original Images")
    plt.figure(figsize=(n, n))
    plt.imshow(canvas_orig, origin="upper", cmap="gray")
    plt.show()

    print("Reconstructed Images")
    plt.figure(figsize=(n, n))
    plt.imshow(canvas_recon, origin="upper", cmap="gray")
    plt.show()
'''

