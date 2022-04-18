import logging
import time

import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.layers import (Conv2D, Dense, Dropout, Flatten, MaxPool2D)
from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D, MaxPool2D
from keras.layers import Activation, Dropout, Flatten, Dense, BatchNormalization
from tensorflow.keras import regularizers
from tensorflow.keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator

import nni

_logger = logging.getLogger("Gemstone Classifier - Alexnet")
_logger.setLevel(logging.INFO)

class AlexNet(Model):
    def __init__(self, conv_size: list, filter_size: list, hidden_size: list, dropout_rate: list):
        super().__init__()

        img_height = img_width = 300
        
        # First Layer
        self.conv1 = Conv2D(input_shape=(img_height, img_width, 3), filters = filter_size[0], kernel_size = conv_size[0], strides = (4, 4), padding = "same")
        self.batch_norm1 = BatchNormalization()
        self.activ1 = Activation("relu")
        self.pool1 = MaxPool2D(pool_size = 2, strides = (2, 2), padding = "same")

        # Second Layer
        self.conv2 = Conv2D(filters = filter_size[1], kernel_size = conv_size[1], strides = (1, 1), padding = "same")
        self.batch_norm2 = BatchNormalization()
        self.activ2 = Activation("relu")
        self.pool2 = MaxPool2D(pool_size = 2, strides = (2, 2), padding = "same")

        # Third Layer
        self.conv3 = Conv2D(filters = filter_size[2], kernel_size = conv_size[2], strides = (1, 1), padding = "same")
        self.batch_norm3 = BatchNormalization()
        self.activ3 = Activation("relu")
        
        # Fourth Layer
        self.conv4 = Conv2D(filters = filter_size[3], kernel_size = conv_size[3], strides = (1, 1), padding = "same")
        self.batch_norm4 = BatchNormalization()
        self.activ4 = Activation("relu")

        # Fifth Layer
        self.conv5 = Conv2D(filters = filter_size[4], kernel_size = conv_size[4], strides = (1, 1), padding = "same")
        self.batch_norm5 = BatchNormalization()
        self.activ5 = Activation("relu")
        self.pool5 = MaxPool2D(pool_size = 2, strides = (2, 2), padding = "same")

        # Flatten Layer
        self.flatten6 = Flatten()
        
        # First FC Layer
        self.fc7 = Dense(units = hidden_size[0], input_shape = (32, 32, 3,))
        self.batch_norm7 = BatchNormalization()
        self.activ7 = Activation("relu")
        self.drop7 = Dropout(dropout_rate[0])
        
        # Second FC Layer
        self.fc8 = Dense(units = hidden_size[1])
        self.batch_norm8 = BatchNormalization()
        self.activ8 = Activation("relu")
        self.drop8 = Dropout(dropout_rate[1])

        # Third FC Layer
        self.fc9 = Dense(units = hidden_size[2])
        self.batch_norm9 = BatchNormalization()
        self.activ9 = Activation("relu")
        self.drop9 = Dropout(dropout_rate[2])

       #Output Layer

        self.fc10 = Dense(units = 80)
        self.batch_norm10 = BatchNormalization()
        self.activ10 = Activation("softmax")

    
    def call(self, x):
        x = self.conv1(x)
        x = self.batch_norm1(x)
        x = self.activ1(x)
        x = self.pool1(x)

        x = self.conv2(x)
        x = self.batch_norm2(x)
        x = self.activ2(x)
        x = self.pool2(x)

        x = self.conv3(x)
        x = self.batch_norm3(x)
        x = self.activ3(x)

        x = self.conv4(x)
        x = self.batch_norm4(x)
        x = self.activ4(x)

        x = self.conv5(x)
        x = self.batch_norm5(x)
        x = self.activ5(x)
        x = self.pool5(x)

        x = self.flatten6(x)

        x = self.fc7(x)
        x = self.batch_norm7(x)
        x = self.activ7(x)
        x = self.drop7(x)

        x = self.fc8(x)
        x = self.batch_norm8(x)
        x = self.activ8(x)
        x = self.drop8(x)

        x = self.fc9(x)
        x = self.batch_norm9(x)
        x = self.activ9(x)
        x = self.drop9(x)
        
        x = self.fc10(x)
        x = self.batch_norm10(x)
        x = self.activ10(x)
        
        return x

class ReportIntermediates(Callback):
    """
    Callback class for reporting intermediate accuracy metrics.
    This callback sends accuracy to NNI framework every 100 steps,
    so you can view the learning curve on web UI.
    If an assessor is configured in experiment's YAML file,
    it will use these metrics for early stopping.
    """
    def on_epoch_end(self, epoch, logs=None):
        """Reports intermediate accuracy to NNI framework"""
        # TensorFlow 2.0 API reference claims the key is `val_acc`, but in fact it's `val_accuracy`
        if 'val_acc' in logs:
            nni.report_intermediate_result(logs['val_acc'])
        else:
            nni.report_intermediate_result(logs['val_accuracy'])


def main(params):

    model = AlexNet(conv_size = [params["conv_size_1"], params["conv_size_2"], params["conv_size_3"], params["conv_size_4"], params["conv_size_5"]],
                    filter_size = [params["filter_size_1"], params["filter_size_2"], params["filter_size_3"], params["filter_size_4"], params["filter_size_5"]],
                    hidden_size = [params["hidden_size_1"], params["hidden_size_2"], params["hidden_size_3"]],
                    dropout_rate = [params["dropout_rate_1"], params["dropout_rate_2"], params["dropout_rate_3"]]
            )

    optimizer = Adam(learning_rate = params["learning_rate"])
    model.compile(optimizer = optimizer, loss = "sparse_categorical_crossentropy", metrics=["accuracy"])
    _logger.info("Model built")

    train_datagen = ImageDataGenerator()
    val_datagen = ImageDataGenerator()
    test_datagen = ImageDataGenerator()

    train_gen = train_datagen.flow_from_directory(
        directory=r"./output/train/",
        target_size=(300, 300),
        color_mode="rgb",
        batch_size=params['batch_size'],
        class_mode="sparse",
        shuffle=True
    )

    val_gen = val_datagen.flow_from_directory(
        directory=r"./output/val/",
        target_size=(300, 300),
        color_mode="rgb",
        batch_size=params['batch_size'],
        class_mode="sparse",
        shuffle=True
    )

    test_gen = test_datagen.flow_from_directory(
        directory=r"./output/test/",
        target_size=(300, 300),
        color_mode="rgb",
        batch_size=1,
        class_mode="sparse",
        shuffle=False
    )
    
    # Reseting data generator
    test_gen.reset()

    _logger.info("Starting trainning")

    model.fit(
        train_gen,
        steps_per_epoch = train_gen.n // train_gen.batch_size,
        batch_size=params['batch_size'],
        epochs=50,
        verbose=0,
        callbacks=[ReportIntermediates()],
        validation_data = val_gen
    )

    _logger.info("Training completed")
    loss, accuracy = model.evaluate(test_gen, verbose=0)
    _logger.info("Model evaluated")
    
    # send final accuracy to NNI tuner and web UI
    nni.report_final_result(accuracy) 
    _logger.info("Final loss reported: %s", loss)
    _logger.info("Final accuracy reported: %s", accuracy)

    _logger.info("Model summary")
    _logger.info(model.summary())


    filename = time.strftime("%Y%m%d_%H%M%S") + ".h5"
    _logger.info("Saving model with name: " + filename)
    tf.saved_model.save(model, filename)
    

if __name__ == '__main__':
    params = {
        'dropout_rate': 0.5,
        'conv_size': 5,
        'hidden_size': 1024,
        'batch_size': 32,
        'learning_rate': 1e-4,
    }

    # fetch hyper-parameters tuner
    # comment out following two lines to run the code without NNI framework
    tuned_params = nni.get_next_parameter()
    params.update(tuned_params)

    _logger.info('Hyper-parameters: %s', params)
    main(params)
