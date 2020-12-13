# What: Data generation with SenseGen, which takes in user dataset and generates synthetic data
# Where: The code has been heavily modified and parts borrowed from: https://github.com/nesl/sensegen
# Why: Modifying existing code saves time for developing the major components of the system


# Usage example: 
#   import gen_data
#   z = gen_data.gen_data_GAN() #see the arguments below.

import warnings
warnings.filterwarnings('ignore')
import igan_data.data_utils
import igan_data.model_utils
import igan_data.model
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.FATAL)
import numpy as np
import glob
import os, shutil

# hyperparameters: 1. dataset file (numpy) 2. data type (.mat or .csv) 3. number of synthetic sequences to be generated 
# 4. at what epochs to save model 5. training epoch 6. model output dir
# more hyperparameters will be added after mid term

LOG_FILE = 'tensorflow_logger.txt'
LOG_PATH = 'server_data'

# path_to_logger = os.path.join(LOG_PATH, LOG_FILE)
# open(path_to_logger, "w").close()
#
# with open(path_to_logger, "a") as f:
#     f.write('Training...\n')
# print('Training...')
#
# with open(path_to_logger, "a") as f:
#     f.write('Generating synthetic data...\n')
# print('Generating synthetic data...')
#
# with open(path_to_logger, "a") as f:
#     f.write('Done training.\n')
# print('Done training.')
#
# with open(path_to_logger, "a") as f:
#     f.write('Data generated\n')
# print('Data generated')

# open(path_to_logger, "w").close()


def gen_data_GAN(data, 
                 data_type = '.mat', 
                 num_seq = 10, 
                 model_chkpoint = 100,
                 num_epochs = 200,
                 batch_size = 128,
                 out_dir = 'models/'):
    #data = data_utils.load_training_data(data_dir,data_type)
    igan_data.model_utils.reset_session_and_model()
    with tf.Session() as sess:
        train_config = igan_data.model.ModelConfig()
        test_config = igan_data.model.ModelConfig()
        #the following variables will be hypermaters in final project too.
        train_config.learning_rate = 0.003
        train_config.num_layers = 1
        train_config.batch_size = batch_size
        test_config.num_layers = 1
        test_config.batch_size = 1
        test_config.num_steps = 1
        loader = igan_data.data_utils.DataLoader(data=data,batch_size=train_config.batch_size, num_steps=train_config.num_steps)
        train_model = igan_data.model.MDNModel(train_config, True)
        test_model = igan_data.model.MDNModel(test_config, False)
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        print('Training current model...')
        for idx in range(num_epochs):
            epoch_loss = train_model.train_for_epoch(sess, loader)
            print('Epoch: ',idx, ' Loss: ', epoch_loss)
            if (idx+1) % model_chkpoint== 0:
                saver.save(sess, out_dir + 'GAN_models.ckpt', global_step=idx)
        print('Done training current model.')
    ckpt_path = out_dir + 'GAN_models.ckpt-'+str(num_epochs-model_chkpoint)
    igan_data.model_utils.reset_session_and_model()
    fake_list = []
    print('Generating synthetic data for current class...')
    with tf.Session() as sess:
        test_config = igan_data.model.ModelConfig()
        test_config.num_layers = 1
        test_config.batch_size = 1
        test_config.num_steps = 1
        test_model = igan_data.model.MDNModel(test_config, True)
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
    print('Data generated for current class')
    shutil.rmtree('models/')
    os.mkdir('models/')
    return fake_list


def gen_data_multiclass(data,
                        classL,
                        num_classes,
                        num_seq,
                        data_type='.mat',
                        model_chkpoint=5,
                        num_epochs=150):
    _, indices = np.unique(classL, return_index=True)
    indices = np.append(indices,data.shape[0])
    syndata_list =  np.empty((0,data.shape[1]))
    class_list = []
    for i in range(num_classes):
        if indices[i+1]-indices[i] > 128:
            batch_size = 128
        else:
            batch_size = indices[i+1]-indices[i]
        print("Training for class ", classL[indices[i]])
        synthesized_data = gen_data_GAN(data = data[indices[i]:indices[i+1],:],
                     data_type = data_type,
                     num_seq = num_seq[i],
                     model_chkpoint = model_chkpoint,
                     num_epochs = num_epochs,
                     batch_size = batch_size,
                     out_dir = 'models/')
        syndata_list = np.concatenate((syndata_list,synthesized_data))
        class_list.append(np.repeat(classL[indices[i]],num_seq[i]))
    print("Data generation for all classes complete")
    class_list = np.concatenate(class_list).ravel()
    return syndata_list, class_list, num_classes