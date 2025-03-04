from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import pandas as pd
import mysql.connector
import google.generativeai as genai
from io import BytesIO
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

db_config = {
    "host": "128.140.38.157",
    "user": "riyad_codeta",
    "password": "code_ta_24680",
    "database": "code_train"
}

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-1.5-pro-latest') 
    response = model.generate_content([prompt[0], question])
    return response.text.strip()  

def read_sql_query(sql_query, db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        cursor.close()
        connection.close()
        return results, columns 
    except mysql.connector.Error as err:
        return f"Error: {err}"

def send_email(subject, body, recipient_email, attachment_data, file_name, mime_type):
    try:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587

        sender_email = 'riyadehmedov03@gmail.com'  # Sender's email address
        app_password = 'ogfp zzmi uhxh vdkd'  
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        part = MIMEBase('application', mime_type)
        part.set_payload(attachment_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={file_name}")
        msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() 
            server.login(sender_email, app_password) 
            server.sendmail(sender_email, recipient_email, msg.as_string()) 

        return "Email sent successfully!"
    
    except Exception as e:
        return f"Error sending email: {e}"

prompt = [
    """
    Sən İngilis və Azərbaycan dillərində verilən sualları SQL sorğularına çevirən bir mütəxəssissən!
    SQL bazasının adı `code_train` və içində `superstore` adlı cədvəl var.
    Bu cədvəldə aşağıdakı sütunlar mövcuddur: `RowID`, `OrderID`, `OrderDate`, `ShipDate`, 
    `ShipMode`, `CustomerID`, `CustomerName`, `Segment`, `Country`, `City`, `State`, 
    `PostalCode`, `Region`, `ProductID`, `Category`, `SubCategory`, `ProductName`, 
    `Sales`, `Quantity`, `Discount`, və `Profit`.

    Məsələn:
    Nümunə 1 - Bazada neçə sifariş var?  
    SQL sorğusu belə olacaq:  
    SELECT COUNT(*) FROM superstore;

    Nümunə 2 - New York şəhərindəki müştərilərin bütün sifarişlərini göstər?  
    SQL sorğusu belə olacaq:  
    SELECT * FROM superstore WHERE City = "New York";

    Nümunə 3 - 'Furniture' kateqoriyası üzrə ümumi satış məbləği nə qədərdir?  
    SQL sorğusu belə olacaq:  
    SELECT SUM(Sales) FROM superstore WHERE Category = "Furniture";

    **Bu suallar Azərbaycan dilində də verilə bilər. Həmişə SQL sorğusunu düzgün başa düş və cavab ver.**
    SQL kodunun əvvəlində və sonunda ``` simvolları olmamalıdır və cavabda "sql" sözü yazılmamalıdır.
    """
]

st.set_page_config(page_title="SQL Sorğularının İcrası", layout="centered")
st.header("SQL Sorğusu Hazırlama və Nəticə Göndərmə")

st.sidebar.image("LOGO AG.png", use_container_width = True, width = 5)

if 'df' not in st.session_state:
    st.session_state.df = None

question = st.text_input("Sualı daxil edin:", key="input")
submit = st.button("Sualı ver")

if submit and question:
    sql_query = get_gemini_response(question, prompt)
    st.write(f"Hazırlanmış SQL Sorğusu: `{sql_query}`")

    response, columns = read_sql_query(sql_query, db_config)

    if isinstance(response, str) and response.startswith("Error"):
        st.error(response)  
    else:
        st.subheader("Sorğunun Nəticəsi:")
        st.session_state.df = pd.DataFrame(response, columns=columns)
        st.dataframe(st.session_state.df)

        # CSV və Excel üçün yükləmə düymələri əlavə edirik
        csv = st.session_state.df.to_csv(index=False)
        st.download_button(
            label="CSV olaraq yüklə",
            data=csv,
            file_name="result.csv",
            mime="text/csv"
        )

        # Excel yükləmə
        excel = io.BytesIO()
        st.session_state.df.to_excel(excel, index=False)
        excel.seek(0) 

        st.download_button(
            label="Excel olaraq yüklə",
            data=excel,
            file_name='BakuApartmentDataset.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

st.subheader("Nəticəni e-poçtla göndər")

email = st.text_input("Alıcı E-poçtu")
subject = st.text_input("Mövzu")
body = st.text_area("Mesaj Mətni")

send_csv = st.checkbox("CSV göndər")
send_excel = st.checkbox("Excel göndər")

send_button = st.button("E-poçt göndər")

if send_button:
    if email and subject and body:
        if st.session_state.df is not None:  # Ensure df is defined
            if send_csv:
                csv = st.session_state.df.to_csv(index=False)
                email_response = send_email(subject, body, email, csv, "result.csv", "csv")
            elif send_excel:
                excel = io.BytesIO()
                st.session_state.df.to_excel(excel, index=False)
                excel.seek(0)
                email_response = send_email(subject, body, email, excel.read(), "result.xlsx", "vnd.ms-excel")
            else:
                email_response = "Lütfən göndəriləcək fayl növünü seçin."
            st.write(email_response)
        else:
            st.error("Zəhmət olmasa əvvəlcə bir sorğu icra edin.")
    else:
        st.error("Zəhmət olmasa bütün sahələri doldurun.")