from pydub import AudioSegment
import speech_recognition as sr
def tanimoto(s1, s2):
    a, b, c = len(s1), len(s2), 0.0

    for sym in s1:
        if sym in s2:
            c += 1

    return c / (a + b - c)

def norm_docs(norm_doc):
    return norm_doc.replace('проспект','пр-т').replace('бульвар ','б.').replace('проспект','пр-т').replace('площадь','пл.')

def ogg2wav(ofn):
    wfn = ofn.replace('.ogg','.wav')
    segment = AudioSegment.from_file(ofn)
    segment.export(wfn,format='wav')

def speech_to_text():
    ogg2wav('123.ogg')
    r = sr.Recognizer()
    with sr.AudioFile('123.wav') as source:
        audio = r.record(source)
        text = r.recognize_google(audio,language="ru-RU")
        return text
