# ML 2017 hw6
# Matrix Factorization (Train)

import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
import csv
import numpy as np
import keras.backend as K
from keras.layers import Input, Embedding, Flatten, Dense
from keras.layers.merge import dot, add, concatenate
from keras.models import Model, load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from reader import *

DATA_DIR = './data'

def main():
   
    print('============================================================')
    print('Read Data')
    movies, all_genres, n_movies = read_movie(DATA_DIR + '/movies.csv')
    genders, ages, occupations, n_users = read_user(DATA_DIR + '/users.csv')
    train = read_train(DATA_DIR + '/train.csv')
    print('n_movies:', n_movies, ', n_users:', n_users)
    print('Train data len:', len(train))

    print('============================================================')
    print('Preprocess Data')
    user_id, movie_id, user_genders, user_ages, movie_genres, Y_rating = \
        preprocess('train', train, genders, ages, movies)

    n_users = np.max(user_id) + 1
    n_movies = np.max(movie_id) + 1
    n_genders = 2
    
    print('============================================================')
    print('Construct Model')
    EMB_DIM = 1024
    print('Embedding Dimension:', EMB_DIM)
    in_uid = Input(shape=[1], name='UserID')      # user id
    in_mid = Input(shape=[1], name='MovieID')     # movie id
    in_ug = Input(shape=[1], name='UserGender')   # user gender
    in_ua = Input(shape=[1], name='UserAge')      # user age
    in_mg = Input(shape=[18], name='MovieGenre')  # movie genre
    emb_uid = Embedding(n_users, EMB_DIM, embeddings_initializer='random_normal')(in_uid)
    emb_mid = Embedding(n_movies, EMB_DIM, embeddings_initializer='random_normal')(in_mid)
    emb_ug = Embedding(n_genders, EMB_DIM, embeddings_initializer='random_normal')(in_ug)
    fl_uid = Flatten()(emb_uid)
    fl_mid = Flatten()(emb_mid)
    fl_ug = Flatten()(emb_ug)

    fl_mg = Dense(EMB_DIM, activation='linear', name='MovieGenre_dense')(in_mg)

    dot_id = dot(inputs=[fl_uid, fl_mid], axes=1)
    dot_uid_ug = dot(inputs=[fl_uid, fl_ug], axes=1)
    dot_uid_mg = dot(inputs=[fl_uid, fl_mg], axes=1)
    dot_mid_ug = dot(inputs=[fl_mid, fl_ug], axes=1)
    dot_mid_mg = dot(inputs=[fl_mid, fl_mg], axes=1)
    dot_ug_mg = dot(inputs=[fl_ug, fl_mg], axes=1)

    con_dot = concatenate(inputs=[dot_id, dot_uid_ug, dot_uid_mg, dot_mid_ug, \
                                  dot_mid_mg, dot_ug_mg, in_ua] )
    
    dense_dot = Dense(1, activation='linear')(con_dot)

    emb_uid = Embedding(n_users, 1, embeddings_initializer='zeros')(in_uid)
    emb_mid = Embedding(n_movies, 1, embeddings_initializer='zeros')(in_mid)
    bias_uid = Flatten()(emb_uid)
    bias_mid = Flatten()(emb_mid)
    
    out = add(inputs=[bias_uid, bias_mid, dense_dot])

    model = Model(inputs=[in_uid, in_mid, in_ug, in_ua, in_mg], outputs=out)
    model.summary()

    def rmse(y_true, y_pred):
        mse = K.mean((y_pred - y_true) ** 2)
        return K.sqrt(mse)

    model.compile(optimizer='adam', loss='mse', metrics=[rmse])
   
    print('============================================================')
    print('Train Model')
    es = EarlyStopping(monitor='val_rmse', patience=10, verbose=1, mode='min')
    cp = ModelCheckpoint(monitor='val_rmse', save_best_only=True, save_weights_only=False, \
                         mode='min', filepath='mf_model.h5')
    history = model.fit([user_id, movie_id, user_genders, user_ages, movie_genres], Y_rating, \
                        epochs=200, verbose=1, batch_size=10000, validation_split=0.1, callbacks=[es, cp])
    H = history.history
   
    print('============================================================')
    print('Evaluate Model')
    model = load_model('mf_model.h5', custom_objects={'rmse': rmse})
    score = model.evaluate([user_id, movie_id, user_genders, user_ages, movie_genres], Y_rating, \
                           batch_size=10000)
    print('Score:', score)

    print('============================================================')
    print('Save Result')
    np.savez('mf_history.npz', rmse=H['rmse'])


if __name__ == '__main__':
    main()
