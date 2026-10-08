import pandas as pd
from utils.build_prompt import build_prompt
from AI import ask_gemini

df = pd.read_csv("datasets/sales.csv")

prompt = build_prompt(df)

response = ask_gemini(prompt)

print(response)
