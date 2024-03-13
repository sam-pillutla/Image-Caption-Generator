from flask import Flask, request, jsonify
import cv2
import numpy as np
from keras.applications import ResNet50
from keras.layers import Dense, LSTM, TimeDistributed, Embedding, RepeatVector,Concatenate
from keras.models import Sequential, Model
from keras.preprocessing.sequence import pad_sequences
from flask_cors import CORS

from keras.applications import ResNet50

inception_model = ResNet50(include_top=True)
last = inception_model.layers[-2].output # Output of the penultimate layer of ResNet model 
model = Model(inputs=inception_model.input,outputs=last)

vocab = np.load('vocab.npy', allow_pickle=True)   
vocab = vocab.item()
inverse_dict = {v:k for k,v in vocab.items()}

embedding_len = 128
MAX_LEN = 34
vocab_size = 4031

# Model for image feature extraction
img_model = Sequential()
img_model.add(Dense(embedding_len,input_shape=(2048,),activation='relu'))
img_model.add(RepeatVector(MAX_LEN))

# Model for generating captions from image features
captions_model = Sequential()
captions_model.add(Embedding(input_dim=vocab_size+1,output_dim=embedding_len,input_length=MAX_LEN))
captions_model.add(LSTM(256,return_sequences=True))
captions_model.add(TimeDistributed(Dense(embedding_len)))

# Concatenating the outputs of image and caption models
concat_output = Concatenate()([img_model.output,captions_model.output])
# First LSTM Layer
output = LSTM(units=128,return_sequences=True)(concat_output)
# Second LSTM Layer
output = LSTM(units=512,return_sequences=False)(output)
# Output Layer 
output = Dense(units=vocab_size+1,activation='softmax')(output)
# Creating the final model
final_model = Model(inputs=[img_model.input,captions_model.input],outputs=output)
final_model.compile(loss='categorical_crossentropy',optimizer='RMSprop',metrics='accuracy')

final_model.load_weights('image_caption_generator.h5')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/generate', methods=['POST'])
def after():
    global final_model,vocab,inverse_dict,model
    file = request.files['file']

    file.save('static/file.jpg')
    img = cv2.imread('static/file.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img,(224,224,))                    # diff
    img = np.reshape(img,(1,224,224,3))

    test_feature = model.predict(img).reshape(1,2048)
    pred_text = ['startofseq']
    count = 0
    caption = '' # Stores the predicted captions text
    
    while count < 25:
        count += 1
        # Encoding the captions text with numbers
        encoded = []
        
        for i in pred_text:
            encoded.append(vocab[i])
        
        encoded = [encoded]
        # Padding the encoded text sequences to maximum length
        encoded = pad_sequences(encoded,maxlen=34,padding='post',truncating='post')
        pred_idx = np.argmax(final_model.predict([test_feature,encoded])) # Fetching the predicted word index having the maximum probability of occurrence
        sampled_word = inverse_dict[pred_idx] # Extracting the predicted word by its respective index
        # Checking for ending of the sequence
        if sampled_word == 'endofseq':
            break
        caption = caption + ' ' + sampled_word
        pred_text.append(sampled_word)
 
    return jsonify({'caption': caption})


if __name__ == "__main__":
    app.run(port=9090,debug=True) 