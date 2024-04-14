from config import CONFIG
import os
from dotenv import load_dotenv
import sys
import openai

def progbar(cur, total, width, errorOcurred):
  frac = cur/total
  filled_progbar = round(frac * width)
  bar = "=" * filled_progbar + ">" + "." * (width - filled_progbar)
  colored_bar = "\x1b[31m" + bar if errorOcurred else bar
  print('\r', colored_bar, '[{:>7.2%}]'.format(frac), end='')

def load_env():
  load_dotenv(CONFIG.env_path)
  if os.getenv("OPENAI_API_KEY") is not None:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print ("OPENAI_API_KEY is ready!")
  else:
    print("OPENAI_API_KEY environment variable not found, check .env is setup correctly!")
    sys.exit(1)