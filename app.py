import streamlit as st
import urllib3
import requests
from bs4 import BeautifulSoup
#import re
import requests
import html2text
from transformers import pipeline

#from transformers import PegasusTokenizer, PegasusForConditionalGeneration

# Set headers
headers = requests.utils.default_headers()
headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

st.title("🔎 Auto Meta Description Generator")

url = st.text_input("")
if url:
  req = requests.get(url, headers)
  #st.markdown("Status : URL Scraped")
  
  soup = BeautifulSoup(req.content, 'html.parser')
  html = soup.prettify()
  #st.markdown("Status : HTML Parsed")
  
  h = html2text.HTML2Text()
  html_to_text = h.handle(html)
  
  st.text("Status : URL scraped, HTMP Parsed & Cleaned. The content is ready for Summarization.")

  st.caption("Existing Meta Description")
  find_description = soup.find('meta', {'name':'description'})
  existing_description = find_description['content']
  st.write(existing_description)
  
  st.text("Status : Pytorch Summarizer Initiated. It will take around 2 minutes to get up to speed")

  summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base", framework="tf")
  st.text("Status : Pytorch Summarizer is ready to summarize. New Description Generated is being generated. Give a few more seconds.")
  
  
  new_description = summarizer(html_to_text, max_length=160)

  st.caption("New Auto Generated Meta Description - T5")
  st.write(new_description)
