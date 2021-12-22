#import python packages
import streamlit as st
from transformers import pipeline

import requests
from bs4 import BeautifulSoup
import html2text
import requests
import re
import mistletoe
from mistletoe import markdown
from html2text import HTML2Text

#import torch
import json 
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
from transformers import pipeline


from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import nltk
nltk.download('punkt')


st.title("🔎 :pencil: Auto Meta Description Generator")

st.info("Status : Transformers t5-base Summarization Pipeline is being initialized.")
#t5_summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base")
st.success("Status : Successfully Initialized. You will be able to use this for multiple URLs during session.")


url = st.text_input("Enter the URL you want Auto Generated Meta Description for.")


if url:
  # Set headers
  headers = requests.utils.default_headers()
  headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
  
  st.markdown('URL requested')
  req = requests.get(url, headers)

  st.markdown('HTML Parsed')
  soup = BeautifulSoup(req.content, 'html.parser')
  html = soup.prettify()

  full_page_text = html2text.html2text(html)
  st.markdown('HTML converted to Text')
  #st.markdown(full_page_text)
  
  #LANGUAGE = 'english'
  #parser = PlaintextParser.from_string(full_page_text, Tokenizer(LANGUAGE))

  from sumy.summarizers.lsa import LsaSummarizer

  #Summarizer Started
  LSA_summarizer = LsaSummarizer()

  #removing stopwords
  #LSA_summarizer.stop_words = get_stop_words(LANGUAGE)

  #Summarize the document with 15 sentences
  LSA_Summary =LSA_summarizer(parser.document,15)
  

  LSA_Summary_Text = ""

  for each in LSA_Summary:
    LSA_Summary_Text = LSA_Summary_Text + str(each)
  st.info('Generating - LSA based Extractive Summary to use for Abstractive Summurization.')
  st.caption(LSA_Summary_Text)
  
  

  st.header(':pencil2: Generating - Meta Description using Extractive Summary.  It takes 2-3 mins.')
  #new_description = t5_summarizer(LSA_Summary_Text, max_length=160, min_length=30, do_sample=False)

  st.info(':pencil: Here is your New Description')
  st.success(new_description[0]['summary_text'].capitalize())
  
