import streamlit as st
from transformers import pipeline
from bs4 import BeautifulSoup
import requests
import urllib
import re
import mistletoe
import html2text
from mistletoe import markdown
from html2text import HTML2Text

# Set headers
headers = requests.utils.default_headers()
headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

st.text("Transformer just initiated. It will take around 60 seconds for URL input box to show.")
summarizer = pipeline("summarization")


st.title("🔎 Auto Meta Description Generator")

url = st.text_input("")
if url:
  req = requests.get(url, headers)
  soup = BeautifulSoup(req.content, 'html.parser')
  html = soup.prettify()

  def html2md(html):
      parser = HTML2Text()
      parser.ignore_images = True
      parser.ignore_anchors = True
      parser.body_width = 0
      md = parser.handle(html)
      return md

  def html2plain(html):
      # HTML to Markdown
      md = html2md(html)
      # Normalise custom lists
      md = re.sub(r'(^|\n) ? ? ?\\?[•·–-—-*]( \w)', r'\1  *\2', md)
      # Convert back into HTML
      html_simple = mistletoe.markdown(md)
      # Convert to plain text
      soup = BeautifulSoup(html_simple)
      text = soup.getText()
      # Strip off table formatting
      text = re.sub(r'(^|\n)\|\s*', r'\1', text)
      # Strip off extra emphasis
      text = re.sub(r'\*\*', '', text)
      # Remove trailing whitespace and leading newlines
      text = re.sub(r' *$', '', text)
      text = re.sub(r'\n\n+', r'\n\n', text)
      text = re.sub(r'^\n+', '', text)
      return text

  ARTICLE = html2plain(html)
  st.text("Status : URL scraped, HTMP Parsed & Cleaned. The content is ready for Summarization.")
  
  max_chunk = 500

  ARTICLE = ARTICLE.replace('.', '.<eos>')
  ARTICLE = ARTICLE.replace('?', '?<eos>')
  ARTICLE = ARTICLE.replace('!', '!<eos>')

  sentences = ARTICLE.split('<eos>')
  current_chunk = 0 
  chunks = []

  for sentence in sentences:
      if len(chunks) == current_chunk + 1: 
          if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
              chunks[current_chunk].extend(sentence.split(' '))
          else:
              current_chunk += 1
              chunks.append(sentence.split(' '))
      else:
          print(current_chunk)
          chunks.append(sentence.split(' '))

  for chunk_id in range(len(chunks)):
      chunks[chunk_id] = ' '.join(chunks[chunk_id])

  st.text("Status : Text chunking in less than 500 tokens complete.")
  st.text("Status : Summarising each chunk.")
  res = summarizer(chunks, max_length=160, min_length=30, do_sample=False)
  
  res[0]
  ' '.join([summ['summary_text'] for summ in res])
  text = ' '.join([summ['summary_text'] for summ in res])
  st.text("Status : Summaized text from chunks are joined. Now Summarizing for Meta Descrition.")
  final_text = summarizer(text, max_length=160, min_length=30, do_sample=False)
  
  st.markdown("New Auto Generated Meta Description - T5")
  st.write(final_text)
  
  st.markdown("Existing Meta Description")
  find_description = soup.find('meta', {'name':'description'})
  existing_description = find_description['content']
  st.write(existing_description)
