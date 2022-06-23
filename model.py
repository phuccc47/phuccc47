from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.utils.np_utils import to_categorical
import tensorflow as tf
from tensorflow import keras
import pickle
import json
import re

patterns = {
	'[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
	'[đ]': 'd',
	'[èéẻẽẹêềếểễệ]': 'e',
	'[ìíỉĩị]': 'i',
	'[òóỏõọôồốổỗộơờớởỡợ]': 'o',
	'[ùúủũụưừứửữự]': 'u',
	'[ỳýỷỹỵ]': 'y'
}

stop_words = ['bạn', 'ban', 'anh', 'chị', 'chi', 'em', 'shop', 'bot', 'ad']

def convert_to_no_accents(text): 
	output = text
	for regex, replace in patterns.items():
		output = re.sub(regex, replace, output)
		output = re.sub(regex.upper(), replace.upper(), output)
	return output

trains = {}
with open('intents.json', 'r', encoding='utf-8') as json_data:
	intents = json.load(json_data)
	for one_intent in intents['intents']:
		sentences = one_intent['patterns']
		trains[one_intent['tag']] = sentences
# print(trains)
classes = {}
X_train = []
y_train = []
for i, (key, value) in enumerate(trains.items()):
	X_train += [word_tokenize(v, format="text") for v in value] + [convert_to_no_accents(v) for v in value]
	y_train += [i]*len(value)*2
	classes[i] = key

pickle.dump(classes, open("classes.pkl", "wb"))
y_train = to_categorical(y_train)


vectorizer = TfidfVectorizer(lowercase=True, stop_words=stop_words)
print(vectorizer)

# save this
X_train = vectorizer.fit_transform(X_train).toarray()
pickle.dump(vectorizer, open("tfidf_vectorizer.pkl", "wb"))
# print(vectorizer)

print(X_train)
print('shape = ', X_train.shape[1:])
model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(10,activation='relu', input_dim = X_train.shape[1] ))
model.add(tf.keras.layers.Dense(10,activation='relu'))
model.add(tf.keras.layers.Dense(10,activation='relu'))
model.add(tf.keras.layers.Dense(10,activation='relu'))
model.add(tf.keras.layers.Dense(len(y_train[0]), activation='softmax'))
callbacks = [
	keras.callbacks.ModelCheckpoint('model.h5', save_best_only=True),
]
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X_train, y_train, epochs=2000, batch_size=8, callbacks=callbacks)
model.summary()
model.save('model.h5')