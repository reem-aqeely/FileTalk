import pandas as pd
import re


def detect_date_columns(df):

    date_keywords = [
        "date",
        "time",
        "created",
        "updated",
        "modified",
        "joined",
        "birth"
    ]

    for column in df.columns:

        column_name = column.lower()

        # تحويل أعمدة التاريخ
        if any(keyword in column_name for keyword in date_keywords):

            try:
                df[column] = pd.to_datetime(df[column], errors="ignore")

                if pd.api.types.is_datetime64_any_dtype(df[column]):
                    df[column] = df[column].dt.date

            except:
                pass

        # تنظيف النصوص الطويلة و XML
        if df[column].dtype == "object":

            try:

                sample = df[column].dropna().astype(str).head(20)

                if sample.empty:
                    continue

                # يحتوي XML أو HTML
                if sample.str.contains(r"<[^>]+>", regex=True).mean() > 0.5:
                    df.drop(columns=[column], inplace=True)
                    continue

                # روابط
                if sample.str.contains("http", case=False).mean() > 0.5:
                    df.drop(columns=[column], inplace=True)
                    continue

                # نصوص طويلة جداً
                if sample.str.len().mean() > 120:
                    df.drop(columns=[column], inplace=True)
                    continue

            except:
                pass

    # حذف الأعمدة الإدارية
    banned = [
        "id",
        "guid",
        "rowguid",
        "xml",
        "modified",
        "timestamp"
    ]

    remove = []

    for column in df.columns:

        name = column.lower()

        if any(word in name for word in banned):
            remove.append(column)

    df = df.drop(columns=remove, errors="ignore")

    return df
