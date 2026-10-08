import streamlit as st
import pandas as pd
import plotly.express as px


def render():
    st.header("Visualizations")

    if "df" not in st.session_state or "relationships" not in st.session_state:
        st.warning("Please upload a file in the home page first.")
        return

    df = st.session_state["df"]
    relationships = st.session_state["relationships"]

    for relation in relationships:

        title = relation["title"]
        x_column = relation["x"]
        y_column = relation["y"]

        if x_column not in df.columns:
            continue

        if y_column is not None and y_column not in df.columns:
            continue

        st.subheader(title)

        # 🧹 تجهيز نسخة خفيفة ومصفاة من البيانات للرسم السليم
        plot_df = df.copy()

        # 1. إذا كان العمود النصي يحتوي على رموز XML أو روابط مفصلة، نتجاهل رسمه
        sample_x = str(plot_df[x_column].dropna().iloc[0]
                       ) if not plot_df[x_column].dropna().empty else ""
        if sample_x.startswith("<") or sample_x.startswith("http"):
            st.info(f"Skipped rendering {title} (Complex text format)")
            continue

        x_type = plot_df[x_column].dtype

        # 📊 الحالة الأولى: متغير واحد (Histogram)
        if y_column is None:
            fig = px.histogram(
                plot_df,
                x=x_column,
                title=title
            )

        # 📊 الحالة الثانية: متغيرين
        else:
            y_type = plot_df[y_column].dtype

            # رسم خط زمني (Line Chart)
            if (
                pd.api.types.is_datetime64_any_dtype(x_type)
                and
                pd.api.types.is_numeric_dtype(y_type)
            ):
                # تجميع البيانات حسب اليوم لتفادي زحمة الثواني والأجزاء المجهرية
                grouped_df = plot_df.groupby(plot_df[x_column].dt.date)[
                    y_column].mean().reset_index()
                fig = px.line(
                    grouped_df,
                    x=x_column,
                    y=y_column
                )

            # رسم أشرطة (Bar Chart) للمتغيرات النصية
            elif (
                pd.api.types.is_object_dtype(x_type)
                and
                pd.api.types.is_numeric_dtype(y_type)
            ):
                # اقتصار العمود النصي على أول 20 حرف وأعلى 15 فئة لتفادي تداخل المحاور
                plot_df[x_column] = plot_df[x_column].astype(
                    str).str.slice(0, 20)
                top_df = plot_df.groupby(
                    x_column)[y_column].mean().nlargest(15).reset_index()

                fig = px.bar(
                    top_df,
                    x=x_column,
                    y=y_column
                )

            # رسم انتشار (Scatter Plot) للمتغيرات الرقمية
            elif (
                pd.api.types.is_numeric_dtype(x_type)
                and
                pd.api.types.is_numeric_dtype(y_type)
            ):
                fig = px.scatter(
                    plot_df,
                    x=x_column,
                    y=y_column
                )

            else:
                plot_df[x_column] = plot_df[x_column].astype(
                    str).str.slice(0, 20)
                top_df = plot_df.head(20)
                fig = px.bar(
                    top_df,
                    x=x_column,
                    y=y_column
                )

        # تحسين شكل الرسم البياني
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
