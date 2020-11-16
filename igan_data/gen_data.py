# What: Data generation with SenseGen, which takes in user dataset and generates synthetic data
# Where: The code has been heavily modified and parts borrowed from: https://github.com/nesl/sensegen
# Why: Modifying existing code saves time for developing the major components of the system


# Usage example: 
#   import gen_data
#   z = gen_data.gen_data_GAN() #see the arguments below.

import warnings
warnings.filterwarnings('ignore')
import data_utils
import model_utils
import model
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.FATAL)
import numpy as np
import glob
import os

# hyperparameters: 1. dataset file (numpy) 2. data type (.mat or .csv) 3. number of synthetic sequences to be generated 
# 4. at what epochs to save model 5. training epoch 6. model output dir
# more hyperparameters will be added after mid term

def gen_data_GAN(data, 
                 data_type = '.mat', 
                 num_seq = 10, 
                 model_chkpoint = 100,
                 num_epochs = 200, 
                 out_dir = 'models/'):
    #data = data_utils.load_training_data(data_dir,data_type)
    model_utils.reset_session_and_model()
    with tf.Session() as sess:
        train_config = model.ModelConfig()
        test_config = model.ModelConfig()
        #the following variables will be hypermaters in final project too.
        train_config.learning_rate = 0.003
        train_config.num_layers = 1
        train_config.batch_size = 128
        test_config.num_layers = 1
        test_config.batch_size = 1
        test_config.num_steps = 1
        loader = data_utils.DataLoader(data=data,batch_size=train_config.batch_size, num_steps=train_config.num_steps)
        train_model = model.MDNModel(train_config, True)
        test_model = model.MDNModel(test_config, False)
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        print('Training...')
        for idx in range(num_epochs):
            epoch_loss = train_model.train_for_epoch(sess, loader)
            print('Epoch: ',idx, ' Loss: ', epoch_loss)
            if (idx+1) % model_chkpoint== 0:
                saver.save(sess, out_dir + 'GAN_models.ckpt', global_step=idx)
        print('Done training.')
    ckpt_path = out_dir + 'GAN_models.ckpt-'+str(num_epochs-model_chkpoint)
    model_utils.reset_session_and_model()
    fake_list = []
    print('Generating synthetic data...')
    with tf.Session() as sess:
        test_config = model.ModelConfig()
        test_config.num_layers = 1
        test_config.batch_size = 1
        test_config.num_steps = 1
        test_model = model.MDNModel(test_config, True)
        test_model.is_training = False
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        list_of_files = glob.glob(out_dir+'*')
        latest_file = max(list_of_files, key=os.path.getctime)
        t = [pos for pos, char in enumerate(latest_file) if char == '.']
        l, r = latest_file[:t[-1]], latest_file[t[-1]:]
        saver.restore(sess, l)
        for i in range(num_seq):
            fake_data = test_model.predict(sess, data.shape[1])
            fake_list.append(fake_data)
    fake_list = np.array(fake_list) #returns num_seq x data.shape[0] numpy array
    print('Data generated')
    return fake_list