from underthesea import word_tokenize
# things we need for Tensorflow
import tensorflow as tf
import keras
import numpy
import random
import pickle
import json

classes = pickle.load( open( "classes.pkl", "rb" ) )

with open('intents.json', 'r', encoding='utf-8') as json_data:
	intents = json.load(json_data)



model = tf.keras.models.load_model('model.h5')
# model.summary()

vectorizer = pickle.load(open("tfidf_vectorizer.pkl", "rb"))

def classify(sentence):
	sentence = word_tokenize(sentence, format="text")
	results = model.predict(vectorizer.transform([sentence]).toarray())[0]
	results = numpy.array(results)
	idx = numpy.argsort(-results)[0]
	return classes[idx], results[idx]

def response(tag):
	for i in intents['intents']:
		if i['tag'] == tag:
			return random.choice(i['responses'])

if __name__ == '__main__':
	print('Begin chatting: ')
	while True:
		print('Human: ', end=''),
		x = input()
		tag, _ = classify(x)
		print('Bot: ', response(tag))

		