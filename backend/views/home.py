import streamlit as st
import pandas as pd
import json
from utils.cleaning import detect_date_columns
from utils.build_prompt import build_prompt, build_suggested_questions_prompt
from AI import ask_gemini


def get_clean_columns_for_visualization(df):
    """تصفية عامة لجميع أنواع البيانات المعقدة أو المزدحمة لمنع الرسومات المكسورة لأي ملف"""
    valid_cols = []

    for col in df.columns:
        col_str = str(col).lower()

        # 1. استبعاد المعرفات والأعمدة الإدارية المعروفة عالمياً
        if any(k in col_str for k in ['guid', 'xml', 'url', 'html', 'json']):
            continue

        # 2. فحص محتوى البيانات: هل يحتوي على رموز XML أو HTML؟
        sample_vals = df[col].dropna().astype(str).head(20)
        if sample_vals.str.contains(r'<[^>]+>', regex=True).any():
            continue

        # 3. فحص النصوص الطويلة (مثل الأوصاف والتغريدات والنصوص المعقدة)
        if sample_vals.str.len().mean() > 50:
            continue

        # 4. استبعاد الأعمدة التي كل قيمها فريدة ونصوص طويلة (High Cardinality Unique Codes)
        if df[col].dtype == 'object' and df[col].nunique() == len(df) and len(df) > 50:
            continue

        valid_cols.append(col)

    return valid_cols


def render():
    st.title("FileTalk")

    # 🎨 تصغير خط قيم الـ Metrics لتبدو مرتبة ومتناسقة
    st.markdown("""
        <style>
            [data-testid="stMetricValue"] {
                font-size: 28px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Please Upload your CSV/Excel File",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

        # قراءة الملف
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # تحويل أعمدة التاريخ
        df = detect_date_columns(df)

        # 🧹 تحويل شامل لكل التواريخ الدقيقة في DataFrame لتصبح تاريخاً مجرداً (YYYY-MM-DD)
        for col in df.select_dtypes(include=['datetime', 'datetime64']).columns:
            df[col] = pd.to_datetime(df[col]).dt.date

        # حفظ البيانات في الـ Session State
        if "df" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
            st.session_state["df"] = df
            st.session_state["file_name"] = uploaded_file.name

            # 🎯 استخراج الأعمدة الصالحة للرسم البياني عامةً
            vis_cols = get_clean_columns_for_visualization(df)

            # إرسال البيانات إلى Gemini
            with st.spinner("Analyzing your file... Please wait ⏳"):
                prompt = build_prompt(df[vis_cols])
                response = ask_gemini(prompt)

                data = json.loads(response)
                st.session_state["report"] = data["report"]
                st.session_state["relationships"] = data["relationships"]

                # Generate suggested questions
                suggested_prompt = build_suggested_questions_prompt(df)
                st.session_state["suggested_questions"] = json.loads(
                    ask_gemini(suggested_prompt))

    # 🎯 طريقة العرض للتقرير
    if "report" in st.session_state:
        report = st.session_state["report"]
        df = st.session_state["df"]

        # 1. بطاقة الملخص
        st.info(f"📌 **About this Dataset:** {report['dataset_summary']}")

        st.markdown("---")

        # 2. حساب نسبة البيانات المفقودة
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        missing_percentage = (missing_cells / total_cells) * 100

        if missing_percentage == 0:
            data_health_value = "Clean Data 🚀"
        else:
            data_health_value = f"{missing_percentage:.1f}% Missing"

        # 3. عرض البطاقات الثلاث
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="📊 Total Rows", value=f"{df.shape[0]:,}")
        with col2:
            st.metric(label="📋 Total Columns", value=f"{df.shape[1]}")
        with col3:
            st.metric(label="🧹 Data Quality", value=data_health_value)

        # عرض الأعمدة الرئيسية بشكل شارات أنيقة
        st.write("")
        st.markdown("**🔑 Key Focus Columns:** " +
                    " ".join([f"`{col}`" for col in report["key_columns"]]))

        st.markdown("---")

        # 4. الرؤى والتوصيات جنبًا إلى جنب في عمودين
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("💡 Important Insights")
            for insight in report["insights"]:
                st.markdown(f"> 🔹 {insight}")

        with col_right:
            st.subheader("🎯 Actionable Recommendations")
            for recommendation in report["recommendations"]:
                st.success(f"✅ {recommendation}")
