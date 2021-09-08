import urllib
import requests
import re
import requests
from bs4 import BeautifulSoup
import html2text
import mistletoe
from mistletoe import markdown
from html2text import HTML2Text


from transformers import BartTokenizer, BartForConditionalGeneration
import torch

model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

from transformers import pipeline
summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base", framework="tf")


# Set headers
headers = requests.utils.default_headers()
headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

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

  text_ready = html2plain(html)
  st.text("Status : URL scraped, HTMP Parsed & Cleaned. The content is ready for Summarization.")

  st.markdown("Existing Meta Description")
  find_description = soup.find('meta', {'name':'description'})
  existing_description = find_description['content']
  st.write(existing_description)
  
  st.text("Status : Pytorch Summarizer Initiated. It will take around 2 minutes to get up to speed")

  # tokenize without truncation
  inputs_no_trunc = tokenizer(text_ready, max_length=None, return_tensors='pt', truncation=False)

  # get batches of tokens corresponding to the exact model_max_length
  chunk_start = 0
  chunk_end = tokenizer.model_max_length  # == 1024 for Bart
  inputs_batch_lst = []
  while chunk_start <= len(inputs_no_trunc['input_ids'][0]):
      inputs_batch = inputs_no_trunc['input_ids'][0][chunk_start:chunk_end]  # get batch of n tokens
      inputs_batch = torch.unsqueeze(inputs_batch, 0)
      inputs_batch_lst.append(inputs_batch)
      chunk_start += tokenizer.model_max_length  # == 1024 for Bart
      chunk_end += tokenizer.model_max_length  # == 1024 for Bart

  # generate a summary on each batch
  summary_ids_lst = [model.generate(inputs, num_beams=4, max_length=160, early_stopping=True) for inputs in inputs_batch_lst]

  # decode the output and join into one string with one paragraph per summary batch
  summary_batch_lst = []
  for summary_id in summary_ids_lst:
      summary_batch = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_id]
      summary_batch_lst.append(summary_batch[0])
  summary_all = '\n'.join(summary_batch_lst)

  st.markdown("New Auto Generated Meta Description - T5")
  st.write(summary_all)
