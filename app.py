
import streamlit as st
import pandas as pd
import base64
from io import BytesIO

st.set_page_config(page_title="עיבוד נתוני אקסל - סיון אמויאל", layout="centered")

st.title("עיבוד נתוני אקסל - סיון אמויאל")
st.markdown("העלה קובץ אקסל עם נתוני קלט:")

uploaded_file = st.file_uploader("בחר קובץ", type=["xlsx"])

def process_excel(file):
    df_input = pd.read_excel(file, sheet_name=0)
    df_data = pd.read_excel(file, sheet_name=1)

    df_data = df_data.dropna(subset=['מס פוליסה', 'עמלה'])

    merged = df_input.merge(df_data, on='מס פוליסה', how='left')
    grouped = df_data.groupby('מס פוליסה')['עמלה'].apply(lambda x: ', '.join(map(str, x))).reset_index()
    totals = df_data.groupby('מס פוליסה')['עמלה'].sum().reset_index(name='סה"כ עמלות לפוליסה')

    final = df_input.merge(grouped, on='מס פוליסה', how='left')
    final = final.merge(totals, on='מס פוליסה', how='left')
    final = final.rename(columns={'עמלה': 'עמלות'})

    return final

def generate_download_link(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='פלט')
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="פלט_מעובד.xlsx">📥 הורד את הקובץ המעובד</a>'
    return href

if uploaded_file:
    try:
        result_df = process_excel(uploaded_file)
        st.success("✅ הקובץ עובד בהצלחה!")
        st.write(result_df)

        st.markdown(generate_download_link(result_df), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")

# Disclaimer in small font
st.markdown(
    """
    <hr>
    <div style='direction: rtl; text-align: center; font-size: 12px; color: gray;'>
    <strong>כתב ויתור ואזהרת שימוש</strong><br>
    כל הזכויות שמורות ©. אין להעתיק, לשכפל, להפיץ, לתרגם, לעשות שימוש מסחרי או ציבורי בתכני האתר, באפליקציה או בתוצריה, כולם או חלקם, בכל צורה שהיא – ללא קבלת אישור מראש ובכתב מכותב האתר. אי מציאת הכותב איננה מתירה כל זכות לבצע את האמור לעיל.<br><br>
    האחריות הבלעדית לשימוש באפליקציה ו/או בתוצריה חלה על המשתמש בלבד. על המשתמש לבדוק היטב את נכונות, דיוק והתאמה של הפלטים, הנתונים והתוצרים לצרכיו ולוודא כי הם מתאימים למטרותיו לפני כל שימוש בהם.<br><br>
    הכותב ו/או מי מטעמו אינו נושא באחריות לכל נזק, ישיר או עקיף, שייגרם עקב שימוש בשירותי האתר, האפליקציה או בתוצריהם.
    </div>
    """,
    unsafe_allow_html=True
)
