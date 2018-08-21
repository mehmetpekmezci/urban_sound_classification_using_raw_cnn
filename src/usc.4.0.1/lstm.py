#!/usr/bin/env python3
from header import *
from data import *


'''
NUMBER_OF_TIME_SLICES=20
SOUND_RECORD_SAMPLING_RATE=22050
NUMBER_OF_CLASSES=10
LSTM_INPUT_SIZE=4*SOUND_RECORD_SAMPLING_RATE/NUMBER_OF_TIME_SLICES
LSTM_OUTPUT_SIZE=10
LSTM_NUMBER_OF_LAYERS=2
LSTM_SIZE=256
MAX_VALUE_FOR_NORMALIZATION=0
MIN_VALUE_FOR_NORMALIZATION=0
TRAINING_ITERATIONS=2000
MINI_BATCH_SIZE=10
lstm_net = ModelNetwork(in_size = LSTM_INPUT_SIZE,lstm_size = LSTM_SIZE,num_layers = LSTM_NUMBER_OF_LAYERS,out_size = LSTM_OUTPUT_SIZE,session = sess,learning_rate = 0.00001,name = "urban_sound_rnn_network")
'''    
#############################################################################################################
class ModelNetwork:
	def __init__(self, in_size, lstm_size, num_layers, out_size, session, learning_rate=0.0003,time_steps=NUMBER_OF_TIME_SLICES, batch_size=MINI_BATCH_SIZE, name="rnn"):
		self.scope = name
		self.in_size = in_size
		print("self.in_size:")
		print(self.in_size)
		##lstm_size==n_hidden 
		self.lstm_size = lstm_size
		print("self.lstm_size:")
		print(self.lstm_size)
		self.num_layers = num_layers
		print("self.num_layers:")
		print(self.num_layers)
		## out_size == n_classes
		self.out_size = out_size
		print("self.out_size:")
		print(self.out_size)
		self.session = session
		self.learning_rate = tf.constant( learning_rate )
		self.time_steps=time_steps
		print("self.time_steps:")
		print(self.time_steps)
		self.batch_size=batch_size
		print("self.batch_size:")
		print(self.batch_size)
		# Last state of LSTM, used when running the network in TEST mode
		self.lstm_last_state = np.zeros((self.num_layers*2*self.lstm_size,))
		print("self.lstm_last_state.shape:")
		print(self.lstm_last_state.shape)
		
		with tf.variable_scope(self.scope):
			## (batch_size, timesteps, in_size)
			self.x_input = tf.placeholder(tf.float32, shape=(batch_size, self.time_steps, self.in_size), name="input")
			print("self.x_input.shape:")
			print(self.x_input.shape)
			self.y_output = tf.placeholder(tf.float32, shape=(batch_size,self.out_size), name="output")
			print("self.y_output.shape:")
			print(self.y_output.shape)
			self.lstm_init_value = tf.placeholder(tf.float32, shape=(None, self.num_layers*2*self.lstm_size), name="lstm_init_value")
			print("self.lstm_init_value.shape:")
			print(self.lstm_init_value.shape)
			# LSTM
			self.lstm_cells = [ tf.contrib.rnn.BasicLSTMCell(self.lstm_size, forget_bias=1.0, state_is_tuple=False) for i in range(self.num_layers)]
           		 ## state_is_tuple: If True, accepted and returned states are 2-tuples of the c_state and m_state. If False, they are concatenated along the column axis. The latter behavior will soon be deprecated.
			self.lstm = tf.contrib.rnn.MultiRNNCell(self.lstm_cells, state_is_tuple=False)
			self.rnn_out_W = tf.Variable(tf.random_normal( (self.lstm_size, self.out_size), stddev=0.01 ))
			print("self.rnn_out_W.shape:")
			print(self.rnn_out_W.shape)
			self.rnn_out_B = tf.Variable(tf.random_normal( (self.out_size, ), stddev=0.01 ))
			# Iteratively compute output of recurrent network
			outputs, self.lstm_new_state = tf.nn.dynamic_rnn(self.lstm, self.x_input, initial_state=self.lstm_init_value, dtype=tf.float32)
			print("outputs.shape:")
			print(outputs.shape)
			print("self.lstm_new_state.shape:")
			print(self.lstm_new_state.shape)
			# Linear activation (FC layer on top of the LSTM net)
			outputs_reshaped = tf.reshape( outputs, [-1, self.lstm_size] )
			print("outputs_reshaped.shape:")
			print(outputs_reshaped.shape)
			network_output = ( tf.matmul( outputs_reshaped, self.rnn_out_W ) + self.rnn_out_B )
			print("network_output.shape:")
			print(network_output.shape)
			batch_time_shape = tf.shape(outputs)
			self.final_outputs = tf.reshape( tf.nn.softmax( network_output), (batch_time_shape[0], batch_time_shape[1], self.out_size) )
			print("self.final_outputs.shape:")
			print(self.final_outputs.shape)
			## Training: provide target outputs for supervised training.
			#self.y_batch = tf.placeholder(tf.float32, (None, None, self.out_size))
			self.y_batch = tf.placeholder(tf.float32, (None,  self.out_size))
			print("self.y_batch.shape:")
			print(self.y_batch.shape)
			#y_batch_long = tf.reshape(self.y_batch, [-1, self.out_size])
			y_batch_long = self.y_batch
			print("y_batch_long.shape:")
			print(y_batch_long.shape)
			self.cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(logits=network_output, labels=y_batch_long) )
			print("self.cost.shape:")
			print(self.cost.shape)
			#self.train_op = tf.train.RMSPropOptimizer(self.learning_rate, 0.9).minimize(self.cost)
			#self.train_op  = tf.train.AdamOptimizer(self.learning_rate).minimize(self.cost)
			self.train_op  = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(self.cost)
			self.accuracy  = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(network_output,1),tf.argmax(y_batch_long,1)), tf.float32))
	## Input: X is a single element, not a list!
	def test_batch(self, x,y, init_zero_state=True):
		## Reset the initial state of the network.
		if init_zero_state:
			init_value = np.zeros((self.num_layers*2*self.lstm_size,))
		else:
			init_value = self.lstm_last_state
		print("init_value.shape:")
		print(init_value.shape)
		print("x.shape:")
		print(x.shape)
		print("y.shape:")
		print(y.shape)
#x = tf.unstack(x, timesteps, 1)
		out, accuracy = self.session.run([self.final_outputs, self.accuracy], feed_dict={self.x_input:x,self.y_batch:y, self.lstm_init_value:[init_value]   } )
		print("out.shape:")
		print(out.shape)
		print(out)

		return out[-1][-1],accuracy
	## xbatch must be (batch_size, timesteps, input_size)
	## ybatch must be (batch_size, timesteps, output_size)
	def train_batch(self, xbatch, ybatch):
		init_value = np.zeros((xbatch.shape[0], self.num_layers*2*self.lstm_size))
		print("init_value.shape:")
		print(init_value.shape)
		print("xbatch.shape:")
		print(xbatch.shape)
		print("ybatch.shape:")
		print(ybatch.shape)
#x = tf.unstack(x, timesteps, 1)
		accuracy = self.session.run([self.accuracy], feed_dict={self.x_input:xbatch, self.y_batch:ybatch, self.lstm_init_value:init_value   } )
		return accuracy

'''
## RESHAPE EXAMPLES :
------------------------------------------------
# tensor 't' is [1, 2, 3, 4, 5, 6, 7, 8, 9]
# tensor 't' has shape [9]
reshape(t, [3, 3]) ==> [[1, 2, 3],
                        [4, 5, 6],
                        [7, 8, 9]]

# tensor 't' is [[[1, 1], [2, 2]],
#                [[3, 3], [4, 4]]]
# tensor 't' has shape [2, 2, 2]
reshape(t, [2, 4]) ==> [[1, 1, 2, 2],
                        [3, 3, 4, 4]]

# tensor 't' is [[[1, 1, 1],
#                 [2, 2, 2]],
#                [[3, 3, 3],
#                 [4, 4, 4]],
#                [[5, 5, 5],
#                 [6, 6, 6]]]
# tensor 't' has shape [3, 2, 3]
# pass '[-1]' to flatten 't'
reshape(t, [-1]) ==> [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6]

# -1 can also be used to infer the shape

# -1 is inferred to be 9:
reshape(t, [2, -1]) ==> [[1, 1, 1, 2, 2, 2, 3, 3, 3],
                         [4, 4, 4, 5, 5, 5, 6, 6, 6]]
# -1 is inferred to be 2:
reshape(t, [-1, 9]) ==> [[1, 1, 1, 2, 2, 2, 3, 3, 3],
                         [4, 4, 4, 5, 5, 5, 6, 6, 6]]
# -1 is inferred to be 3:
reshape(t, [ 2, -1, 3]) ==> [[[1, 1, 1],
                              [2, 2, 2],
                              [3, 3, 3]],
                             [[4, 4, 4],
                              [5, 5, 5],
                              [6, 6, 6]]]

# tensor 't' is [7]
# shape `[]` reshapes to a scalar
reshape(t, []) ==> 7
'''