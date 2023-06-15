
from flask import Flask, request, jsonify
import speech_recognition as sr
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os
import nltk
app = Flask(__name__)


@app.route('/', methods=['Get','POST'])
def audio_to_sign_language():
     r = sr.Recognizer()

     with sr.Microphone() as source:
         r.adjust_for_ambient_noise(source)
         print("Say something!")
         audio = r.listen(source)
    try:
         text =r.recognize_google(audio)
        text = "Hello World"


        print(text)
    except sr.UnknownValueError:
        return jsonify({'error': 'speech not recognized'}), 400

    # preprocess text
    text = text.lower()
    words = word_tokenize(text)
    stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've",'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have',  'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])
   # filtered_text = [lr.lemmatize(w) for w in words if w not in stop_words]

    tagged = nltk.pos_tag(words)
    tense = {}
    tense["future"] = len([word for word in tagged if word[1] == "MD"])
    tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]])
    tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
    tense["present_continuous"] = len([word for word in tagged if word[1] in ["VBG"]])

    lr = WordNetLemmatizer()
    filtered_text = []
    for w, p in zip(words, tagged):
        if w not in stop_words:
            if p[1] == 'VBG' or p[1] == 'VBD' or p[1] == 'VBZ' or p[1] == 'VBN' or p[1] == 'NN':
                filtered_text.append(lr.lemmatize(w, pos='v'))
            elif p[1] == 'JJ' or p[1] == 'JJR' or p[1] == 'JJS' or p[1] == 'RBR' or p[1] == 'RBS':
                filtered_text.append(lr.lemmatize(w, pos='a'))

            else:
                filtered_text.append(lr.lemmatize(w))

    words = filtered_text
    temp = []
    for w in words:
        if w == 'I':
            temp.append('Me')
        else:
            temp.append(w)
    words = temp
    probable_tense = max(tense, key=tense.get)

    if probable_tense == "past" and tense["past"] >= 1:
        temp = ["Before"]
        temp = temp + words
        words = temp
    elif probable_tense == "future" and tense["future"] >= 1:
        if "Will" not in words:
            temp = ["Will"]
            temp = temp + words
            words = temp
        else:
            pass
    elif probable_tense == "present":
        if tense["present_continuous"] >= 1:
            temp = ["Now"]
            temp = temp + words
            words = temp


    # generate sign language animations
    animations = []
    for word in filtered_text:
        path = f"assets/{word}.mp4"
        f = os.path.exists(path)
        if not f:
            for c in word:
                animations.append(c)
        else:
            animations.append(word)

    return jsonify({'animations': animations}), 200


if __name__ == '__main__':
    app.run(debug=True)
