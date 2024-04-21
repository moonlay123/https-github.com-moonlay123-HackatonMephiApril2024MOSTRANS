from dateparser.search import search_dates
from googletrans import Translator
from timefhuman import timefhuman
from datetime import datetime,timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX
from utils import norm_docs
from config import *
from aiogram import Bot, Dispatcher, F
from thefuzz import fuzz
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import stanza,pymorphy3,sys,logging,spacy, pandas as pd, asyncio,io,soundfile as sf,librosa
import speech_recognition as sr
from utils import speech_to_text
# logging.disable(sys.maxsize)
morph = pymorphy3.MorphAnalyzer()
bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer('Пришлите фразу с запросом по пассажиропотоку!')
    await state.clear()

@dp.message(F.voice)
async def get_audio(message: Message, state: FSMContext):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "123.ogg")
    await message.answer('Приступил к обработке!')
    #date extractor
    dataframe1 = pd.read_excel('пп_станции.xlsx')
    some_date = datetime(2024, 4, 3)
    now_date = datetime.now()
    delta_days = (now_date-some_date).days
    date_nlp = spacy.load("en_core_web_sm")

    text = speech_to_text()
    text = text.replace('.','-').replace('/','-')
    translator = Translator()
    translated_text = translator.translate(text).text
    flagishe = 0

    dates = []
    doc = date_nlp(translated_text)
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            try:
                if 'after' in translated_text or 'ago' in translated_text or ' in ' in translated_text :
                        n_t = search_dates(translated_text)
                else:
                    dates.append(timefhuman(ent.text,now=some_date))
                    flagishe = 1
            except:
                pass

    k = ''
    if isinstance(dates,list):
            if len(dates)>0:
                k = dates
            else:
                n_t = search_dates(translated_text)
                if n_t != None:
                    if len(n_t)>1:
                        k = n_t[1][1]
                    else:
                        k = n_t[0][1]
                else:
                    await message.answer('Отсутвует дата!')
    else:
        k = dates

    if k != '':
        extr_date = ''
        if isinstance(k,list):
            if len(k)>1:
                for el in k:
                    extr_date = el
            else:
                extr_date = k[0]
        else:
            extr_date = k

        #metro extractor
        stanza.download('ru') 
        nlp = stanza.Pipeline('ru') 
        doc = nlp(text)

        adress = ''
        for el in doc.sentences:
            for ent in el.entities:
                if (ent.type in ('LOC')):
                    adress = ent.text

        #get peoples
        if adress == '' or extr_date == '':
            await message.answer('Нет даты или адреса! Попробуйте добавить ключевый слова!')
        else:
            norm_doc = morph.parse(adress)[0].normal_form
            norm_doc = norm_docs(norm_doc)
            best_a = 0
            best_el = ''
            for el in dataframe1['Станция']:
                koef = fuzz.token_sort_ratio(norm_doc,el)
                if koef>best_a:
                    best_a = koef
                    best_el = el

        if (datetime.now() - extr_date).days >=0:
            exel_date = extr_date.replace(hour=0,minute=0,second=0,microsecond=0)
            if flagishe == 0:
                exel_date = exel_date-timedelta(days=delta_days)
            await message.answer(f"📒<b>{int(dataframe1[exel_date][dataframe1.index[dataframe1['Станция']==best_el]])}</b> человек📒\nМесто: <b>{best_el}</b>\nДата:<b>{exel_date}</b>",parse_mode='html')
        else:
            data = pd.read_excel('пп_станции.xlsx')

            data.set_index('Станция', inplace=True)

            def predict_passenger_flow(station_name, target_date):
                station_data = data.loc[station_name][3:]
                steps = int((target_date-some_date).days)+1
                model = SARIMAX(station_data.astype(float), order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
                model_fit = model.fit(disp=False)
                prediction = list(model_fit.forecast(steps=steps))[-1]
                return prediction
            predicted_flow = predict_passenger_flow(best_el, extr_date.replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=delta_days))
            await message.answer(f'🔮<b>{int(predicted_flow)}</b> человек 🔮\nМесто: <b>{best_el}</b>\nДата: <b>{extr_date.replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=delta_days)}</b>',parse_mode='html')
    else:
        await message.answer('smth was wrong')

@dp.message()
async def extractor(message: Message, state: FSMContext):
    await message.answer('Приступил к обработке!')
    #date extractor
    dataframe1 = pd.read_excel('пп_станции.xlsx')
    some_date = datetime(2024, 4, 3)
    now_date = datetime.now()
    delta_days = (now_date-some_date).days
    date_nlp = spacy.load("en_core_web_sm")

    text = message.text
    text = text.replace('.','-').replace('/','-')
    translator = Translator()
    translated_text = translator.translate(text).text
    flagishe = 0

    dates = []
    doc = date_nlp(translated_text)
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            try:
                if 'after' in translated_text or 'ago' in translated_text or ' in ' in translated_text :
                        n_t = search_dates(translated_text)
                else:
                    dates.append(timefhuman(ent.text,now=some_date))
                    flagishe = 1
            except:
                pass

    k = ''
    if isinstance(dates,list):
            if len(dates)>0:
                k = dates
            else:
                n_t = search_dates(translated_text)
                if n_t != None:
                    if len(n_t)>1:
                        k = n_t[1][1]
                    else:
                        k = n_t[0][1]
                else:
                    await message.answer('Отсутвует дата!')
    else:
        k = dates

    if k != '':
        extr_date = ''
        if isinstance(k,list):
            if len(k)>1:
                for el in k:
                    extr_date = el
            else:
                extr_date = k[0]
        else:
            extr_date = k

        #metro extractor
        stanza.download('ru') 
        nlp = stanza.Pipeline('ru') 
        doc = nlp(text)

        adress = ''
        for el in doc.sentences:
            for ent in el.entities:
                if (ent.type in ('LOC')):
                    adress = ent.text

        #get peoples
        if adress == '' or extr_date == '':
            await message.answer('Нет даты или адреса! Попробуйте добавить ключевый слова!')
        else:
            norm_doc = morph.parse(adress)[0].normal_form
            norm_doc = norm_docs(norm_doc)
            best_a = 0
            best_el = ''
            for el in dataframe1['Станция']:
                koef = fuzz.token_sort_ratio(norm_doc,el)
                if koef>best_a:
                    best_a = koef
                    best_el = el

        if (datetime.now() - extr_date).days >=0:
            exel_date = extr_date.replace(hour=0,minute=0,second=0,microsecond=0)
            if flagishe == 0:
                exel_date = exel_date-timedelta(days=delta_days)
            await message.answer(f"📒<b>{int(dataframe1[exel_date][dataframe1.index[dataframe1['Станция']==best_el]])}</b> человек📒\nМесто: <b>{best_el}</b>\nДата:<b>{exel_date}</b>",parse_mode='html')
        else:
            data = pd.read_excel('пп_станции.xlsx')

            data.set_index('Станция', inplace=True)

            def predict_passenger_flow(station_name, target_date):
                station_data = data.loc[station_name][3:]
                steps = int((target_date-some_date).days)+1
                model = SARIMAX(station_data.astype(float), order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
                model_fit = model.fit(disp=False)
                prediction = list(model_fit.forecast(steps=steps))[-1]
                return prediction
            predicted_flow = predict_passenger_flow(best_el, extr_date.replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=delta_days))
            await message.answer(f'🔮<b>{int(predicted_flow)}</b> человек 🔮\nМесто: <b>{best_el}</b>\nДата: <b>{extr_date.replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=delta_days)}</b>',parse_mode='html')
    else:
        await message.answer('smth was wrong')

##############################START##################################
async def main():
    await dp.start_polling(bot,allowed_updates=["message", "inline_query", "chat_member",'voice','audio'])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())