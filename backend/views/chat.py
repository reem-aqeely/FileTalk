import streamlit as st
import pandas as pd
import json
from utils.build_prompt import build_pandas_prompt, build_explanation_prompt
from AI import ask_gemini


def render():
    st.header("💬 Ask Your Data")

    if "df" not in st.session_state:
        st.warning("Please upload a file in the home page first.")
        return

    df = st.session_state["df"]
    suggested_questions = st.session_state.get("suggested_questions", [])

    if "user_question" not in st.session_state:
        st.session_state["user_question"] = ""

    def update_question():
        if st.session_state.get("selected_pill"):
            st.session_state["user_question"] = st.session_state["selected_pill"]

    question = st.text_input(
        "Ask anything about your dataset...",
        key="user_question"
    )

    selected = st.pills(
        "💡 Try asking:",
        suggested_questions,
        key="selected_pill",
        on_change=update_question
    )

    if selected:
        question = selected

    if question:

        pandas_prompt = build_pandas_prompt(df, question)
        raw_code = ask_gemini(pandas_prompt)

        # 🧹 تنظيف النص المرتجع من علامات markdown
        code = raw_code.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()

        st.write("Question:", question)

        try:
            if "df" not in code:
                st.error("Invalid code generated.")

            else:
                result = eval(code)

                st.subheader("Answer")

                if isinstance(result, (int, float, str, bool, pd.Timestamp)):
                    st.text(f"{result}")

                elif isinstance(result, pd.DataFrame) and result.shape == (1, 1):
                    st.text(f"{result.iloc[0, 0]}")

                elif isinstance(result, pd.Series) and len(result) == 1:
                    st.text(f"{result.iloc[0]}")

                elif isinstance(result, pd.Series):
                    st.dataframe(result.to_frame())

                elif isinstance(result, pd.DataFrame):
                    st.dataframe(result)

                else:
                    st.write(result)

                exp_prompt = build_explanation_prompt(question, result)
                explanation = ask_gemini(exp_prompt)
                st.info(f"💡 {explanation}")

        except Exception as e:
            st.error(f"Could not execute query: {e}")
