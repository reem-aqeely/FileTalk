def build_pandas_prompt(df, question):

    columns = "\n".join(df.columns)
    types = df.dtypes.to_string()
    sample = df.head(5).to_string()

    prompt = f"""
You are an expert Python Pandas developer.

The dataframe name is df.

Dataset Columns:
{columns}

Column Types:
{types}

Sample Data:
{sample}

User Question:
{question}

Task:
Return ONLY ONE line of valid Python Pandas code that answers the user's question.

Rules:
- Return ONLY executable Pandas code.
- Do NOT use markdown.
- Do NOT explain.
- Do NOT return JSON.
- Use ONLY the existing dataframe named df.
- Use the exact dataset column names.
- If the question asks for top/bottom items, return ONLY the identifying column and the requested metric.
- If multiple values are requested, return a clean DataFrame or Series.
- Use the most appropriate Pandas operation (filtering, sorting, grouping, aggregation, counting or statistics).
"""

    return prompt


def build_prompt(df):

    columns = "\n".join(df.columns)
    types = df.dtypes.to_string()
    sample = df.head().to_string()

    prompt = f"""
You are an expert data analyst and visualization specialist.

Analyze the dataset and return ONLY valid JSON.

Dataset Columns:
{columns}

Column Types:
{types}

Sample Data:
{sample}

Return this JSON:

{{
  "report": {{
      "dataset_summary": "",
      "key_columns": [
          "",
          "",
          ""
      ],
      "insights": [
          "",
          "",
          ""
      ],
      "recommendations": [
          "",
          ""
      ]
  }},
  "relationships": [
      {{
          "title": "",
          "x": "",
          "y": "",
          "chart_type": ""
      }},
      {{
          "title": "",
          "x": "",
          "y": "",
          "chart_type": ""
      }},
      {{
          "title": "",
          "x": "",
          "y": "",
          "chart_type": ""
      }}
  ]
}}

Rules:

- Dataset summary must be no more than 2 sentences.
- Choose only the 3 most important columns.
- Insights should contain useful observations from the sample.
- Recommendations should be practical.

Visualization Rules:

- Every relationship MUST include:
    - title
    - x
    - y
    - chart_type

Allowed chart_type values:

- "bar"
- "line"
- "pie"
- "histogram"

Choose ONLY charts that are clear and meaningful.

Choose:
- categorical vs numeric → bar
- date vs numeric → line
- single categorical column → pie
- single numeric column → histogram

Never choose:
- scatter charts
- ID columns
- GUID columns
- XML columns
- HTML columns
- URL columns
- very long text columns
- metadata columns
- ModifiedDate
- rowguid

Return ONLY valid JSON.
Do NOT use markdown.
"""

    return prompt


def build_chat_prompt(df, question):

    columns = "\n".join(df.columns)
    types = df.dtypes.to_string()
    sample = df.head(10).to_string()

    prompt = f"""
You are an expert AI Data Analyst.

Dataset Information

Rows:
{df.shape[0]}

Columns:
{df.shape[1]}

Column Names:
{columns}

Column Types:
{types}

Sample Data:
{sample}

User Question:
{question}

Rules:

- Answer ONLY using the uploaded dataset.
- Never invent information.
- If the answer cannot be determined, say:
"I cannot determine that from the uploaded dataset."
- Keep the answer short and direct.
"""

    return prompt


def build_suggested_questions_prompt(df):

    columns = "\n".join(df.columns)
    types = df.dtypes.to_string()

    prompt = f"""
You are an AI Data Analyst.

Dataset Columns:
{columns}

Column Types:
{types}

Generate 5 useful questions that fit THIS dataset.

Rules:

- Use the actual column names.
- Make the questions useful.
- Return ONLY a JSON array.
- Do NOT explain.
- Do NOT use markdown.

Example:

[
    "Question 1",
    "Question 2",
    "Question 3",
    "Question 4",
    "Question 5"
]
"""

    return prompt


def build_explanation_prompt(question, result):

    prompt = f"""
You are an expert AI Data Analyst.

User Question:
{question}

Calculated Result:
{result}

Rules:

- Explain the result in ONE short sentence.
- Be direct.
- Do not add introductions.
"""

    return prompt
