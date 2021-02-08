import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia

import pandas as pd
import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier
from sklearn.metrics import confusion_matrix,accuracy_score

nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


def inicializar():
    # mudar a voz
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    #engine.say('Olá, eu sou Bela, o que posso fazer por você?')
    engine.say('Hi, im jane, what can i do for you?')
    engine.runAndWait()


def ouvir():
    try:
        with sr.Microphone() as source:
            command = ''
            listener.adjust_for_ambient_noise(source)
            #print('Ouvindo...')
            print('listening...')
            voice = listener.listen(source)
            command = listener.recognize_google(voice) #,language='pt-BR'
            command = command.lower()

    except:
        pass
    return command


def talk(text):
    engine.say(text)
    engine.runAndWait()
    print(text)


def rodar():
    command = ouvir()

    if 'hey jane' in command:
        command = command.replace('hey jane', '')
        if 'say' in command:
            command = command.replace('say', '')
            command = command.strip()
            talk(command)
        elif 'play' in command:
            song = command.replace('play', '')
            song = song.strip()
            talk('playing ' + song)
            pywhatkit.playonyt(song)
        elif 'time' in command:
            hora = datetime.datetime.now().strftime('%T')
            talk('it is ' + hora)
        elif 'search' in command:
            pesquisa = command.replace('search', '')
            pesquisa = pesquisa.strip()
            talk('searching ' + pesquisa)
            pesquisa = wikipedia.summary(pesquisa,1)
            talk('acording to the wikipedia, ' + pesquisa)
    elif 'so jane' in command:
        command = command.replace('so jane', '')
        #talk(command)
        command = command.strip()

        new_msg = command
        new_msg = re.sub('[^a-zA-Z]', ' ', new_msg)
        new_msg = new_msg.lower()
        new_msg = new_msg.split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        all_stopwords.remove('not')
        new_msg = [ps.stem(word) for word in new_msg if not word in set(all_stopwords)]
        new_msg = ' '.join(new_msg)
        new_corpus = [new_msg]
        new_X_test = cv.transform(new_corpus).toarray()
        new_y_pred = classifier.predict(new_X_test)
        #talk(new_y_pred)

        advice(new_y_pred)


def advice(feeling):
    if feeling == 'fear':
        talk('dont be afraid, you are going to be fine')
    elif feeling == 'joy':
        talk('fantastic, im happy that you are happy')
    elif feeling == 'anger':
        talk('relax, dont lose your head with that')
    elif feeling == 'sadness':
        talk('please, dont be sad, things will get better, I promiss')
    elif feeling == 'surprise':
        talk('I can feel that you are really surprised, arent you?')
    elif feeling == 'love':
        talk('I love this love feeling')

#----------------------------------------------------------------------------------------------------------------------
listener = sr.Recognizer()
engine = pyttsx3.init()
#wikipedia.set_lang("pt")

dataset = pd.read_csv("C:/Users/Lucio/PycharmProjects/pythonProject/Python/Jane_feeling_bot_NLP/src/train_feeling.csv")
corpus = []

for i in range(0,18021):
    data = re.sub('[^a-zA-Z]', ' ', dataset["Frase"][i])
    data = data.lower()
    data = data.split()
    ps = PorterStemmer()
    all_stopwords = stopwords.words('english')
    all_stopwords.remove('not')
    #all_stopwords.remove("couldn't")
    all_stopwords.remove("didn't")
    #all_stopwords.remove("doesn't")
    all_stopwords.remove("don't")
    data = [ps.stem(word) for word in data if not word in set(all_stopwords)]
    data = ' '.join(data)
    corpus.append(data)

cv = CountVectorizer(max_features= 1500)
x = cv.fit_transform(corpus).toarray()
y = dataset.iloc[:, -1].values

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

classifier = CatBoostClassifier()
classifier.fit(x_train,y_train)

y_pred = classifier.predict(x_test)
cm = confusion_matrix(y_test,y_pred)
print(cm)
print(accuracy_score(y_test,y_pred))

inicializar()

while True:
    rodar()