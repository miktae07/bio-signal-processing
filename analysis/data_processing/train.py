from keras.layers import Dense, Convolution1D, MaxPool1D, Flatten, Dropout, Input, Add, concatenate, Conv1D 
from keras.layers.normalization import BatchNormalization
from keras.models import Model
from keras.callbacks import EarlyStopping, ModelCheckpoint
import keras

def inception_module(input_tensor, filters):
    conv1 = Convolution1D(filters, (1), activation='relu', padding='same')(input_tensor)
    conv3 = Convolution1D(filters, (3), activation='relu', padding='same')(input_tensor)
    conv5 = Convolution1D(filters, (5), activation='relu', padding='same')(input_tensor)
    pool = MaxPool1D(pool_size=(3), strides=(1), padding='same')(input_tensor)
    output = concatenate([conv1, conv3, conv5, pool], axis=-1)
    return output

def residual_block(input_tensor, filters):
    # Reduce input dimensions to match the output dimensions
    shortcut = Conv1D(filters, (1), activation='relu', padding='same')(input_tensor)
    
    conv = Convolution1D(filters, (3), activation='relu', padding='same')(input_tensor)
    conv = BatchNormalization()(conv)
    conv = Convolution1D(filters, (3), activation='relu', padding='same')(conv)
    conv = BatchNormalization()(conv)
    
    output = Add()([shortcut, conv])
    return output

def network(X_train, y_train, X_test, y_test):
    im_shape = (X_train.shape[1], 1)
    inputs_cnn = Input(shape=(im_shape), name='inputs_cnn')
    
    # Inception module followed by residual block
    inception = inception_module(inputs_cnn, 64)
    residual = residual_block(inception, 64)
    
    pool1 = MaxPool1D(pool_size=(3), strides=(2), padding="same")(residual)
    
    # Additional Inception module
    inception2 = inception_module(pool1, 128)
    
    pool2 = MaxPool1D(pool_size=(2), strides=(2), padding="same")(inception2)
    
    flatten = Flatten()(pool2)
    dense_end1 = Dense(64, activation='relu')(flatten)
    dense_end2 = Dense(32, activation='relu')(dense_end1)
    main_output = Dense(5, activation='softmax', name='main_output')(dense_end2)
    
    model = Model(inputs=inputs_cnn, outputs=main_output)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=8),
        ModelCheckpoint(filepath='best_model.h5', monitor='val_loss', save_best_only=True)
    ]

    history = model.fit(X_train, y_train, epochs=40, callbacks=callbacks, batch_size=32, validation_data=(X_test, y_test))
    model.load_weights('best_model.h5')
    
    return model, history
print("done")