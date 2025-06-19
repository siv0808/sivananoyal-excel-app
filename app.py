
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="עיבוד נתונים ועמלות אקסל - סיון אמויאל")
st.title("עיבוד נתונים ועמלות אקסל - סיון אמויאל")

uploaded_file = st.file_uploader("העלה קובץ אקסל", type=["xlsx"])

if uploaded_file is not None:
    try:
        # קריאת הגיליונות
        df1 = pd.read_excel(uploaded_file, sheet_name=0)
        df2 = pd.read_excel(uploaded_file, sheet_name=1)

        # שינוי שמות העמודות בעברית
        df1.columns = ['מספר פוליסה']
        df2.columns = ['מספר פוליסה', 'עמלה']

        # המרת עמודת "עמלה" למספרים, הסרת תאריכים או תווים חריגים
        df2['עמלה'] = pd.to_numeric(df2['עמלה'], errors='coerce')

        # קיבוץ וסיכום העמלות לפי מספר פוליסה
        df_sum = df2.groupby('מספר פוליסה')['עמלה'].sum().reset_index()
        df_sum.rename(columns={'עמלה': 'סהכ_עמלות'}, inplace=True)

        # חיבור כל העמלות לפי פוליסה למחרוזת מופרדת בפסיקים
        df_joined = df2.groupby('מספר פוליסה')['עמלה'].apply(
            lambda x: ', '.join(str(v) for v in x.dropna())
        ).reset_index()
        df_joined.rename(columns={'עמלה': 'עמלות'}, inplace=True)

        # מיזוג הכל
        result = df1.merge(df_joined, on='מספר פוליסה', how='left').merge(df_sum, on='מספר פוליסה', how='left')

        # הצגת הטבלה
        st.dataframe(result)

        # המרה לאקסל
        def convert_df(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        st.download_button(
            label="📥 הורד קובץ אקסל מעובד",
            data=convert_df(result),
            file_name="processed_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("✅ העיבוד הושלם בהצלחה! ניתן להוריד את הקובץ המעובד.")

    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")

st.markdown("---")
st.markdown("<p style='font-size:12px; text-align:center;'>כל הזכויות שמורות - ym & סיון אמויאל</p>", unsafe_allow_html=True)
