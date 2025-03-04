import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px


df = pd.read_excel('walmart.xlsx')

st.sidebar.title("Filtrlər")

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['timestamp'] = df['timestamp'].dt.date
df['discount'] = df['discount'].astype('float')

price_min, price_max = int(df['final_price'].min()), int(df['final_price'].max())
price_filter = st.sidebar.slider("Qiymət (₼)", min_value=price_min, max_value=price_max, value=(price_min, price_max), format="₼%d")

date_min, date_max = df['timestamp'].min(), df['timestamp'].max()
date_filter = st.sidebar.slider(
    "Tarix Aralığı",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max),
)

available_for_delivery = st.sidebar.multiselect('Çatdırılma', options=['Bəli', 'Xeyr'], default=['Bəli', 'Xeyr'])
available_for_pickup = st.sidebar.multiselect('Daşınma', options=['Bəli', 'Xeyr'], default=['Bəli', 'Xeyr'])
is_returnable = st.sidebar.multiselect('Dönə bilən', options=['Bəli', 'Xeyr'], default=['Bəli', 'Xeyr'])

discount_min, discount_max = int(df['discount'].min()), int(df['discount'].max())
discount_filter = st.sidebar.slider("Endirim (₼)", min_value=discount_min, max_value=discount_max, value=(discount_min, discount_max), format="₼%d")

free_returns_filter = st.sidebar.multiselect('Pulsuz Geri Qaytarma', options=['Free 90-day returns', 'Devoluciones sin costo en 30 días',
       'Devoluciones sin costo en 90 días', 'Free 30-day returns',
       'Free 45-day returns', 'Not Returnable', 'Return policy'], default=['Free 90-day returns', 'Devoluciones sin costo en 30 días',
       'Devoluciones sin costo en 90 días', 'Free 30-day returns',
       'Free 45-day returns', 'Not Returnable', 'Return policy'])

rating_min, rating_max = float(df['rating'].min()), float(df['rating'].max())
rating_filter = st.sidebar.slider("Qiymətləndirmə", min_value=rating_min, max_value=rating_max, value=(rating_min, rating_max), format="%.1f")

filtered_df = df[
    (df['final_price'] >= price_filter[0]) & (df['final_price'] <= price_filter[1]) &
    (df['timestamp'] >= date_filter[0]) & (df['timestamp'] <= date_filter[1]) &
    (df['available_for_delivery'].isin(available_for_delivery)) &
    (df['available_for_pickup'].isin(available_for_pickup)) &
    (df['is_returnable'].isin(is_returnable)) &
    (df['discount'] >= discount_filter[0]) & (df['discount'] <= discount_filter[1]) &
    (df['free_returns'].isin(free_returns_filter)) &
    (df['rating'] >= rating_filter[0]) & (df['rating'] <= rating_filter[1])
]


st.title("🏪 Walmart satışları")

# Ortalama satışın hesablanması
average_sales = f"₼{df.groupby(by=['timestamp'])['final_price'].mean().mean():,.2f}"
average_review_count = df.groupby(by=['timestamp'])['review_count'].mean().mean().round(0)
product_count = df['product_id'].nunique()

# Metrik kart funksiyası
def metric_card(label, value):
    st.markdown(
        f"""
        <div style="text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 10px; background-color:rgb(2, 13, 24);">
            <p style="font-size: 18px; color:rgb(153, 206, 250); font-weight: bold; margin: 0;">{label}</p>
            <p style="font-size: 24px; color:rgb(255, 223, 223); margin: 0;">{value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 3 sütunlu göstəricilər
col1, col2, col3 = st.columns(3)

with col1:
    metric_card("Ortalama Satış", average_sales)

with col2:
    metric_card("Ortalama Rəy Sayı", average_review_count)

with col3:
    metric_card("Məhsul Sayı", product_count)


# Məlumatların çevrilməsi
df["final_price"] = df["final_price"].astype(float)
df["initial_price"] = df["initial_price"].astype(float)
df["discount"] = df["discount"].astype(float)
df["rating"] = df["rating"].astype(float)

# Çatdırılma və daşınma sütunlarını çevirmək
df["available_for_delivery"] = df["available_for_delivery"].map({"Bəli": 1, "Xeyr": 0})
df["available_for_pickup"] = df["available_for_pickup"].map({"Bəli": 1, "Xeyr": 0})


# --- Brendlər Üzrə Analiz ---
st.header('📌 Brendlər Üzrə Analiz')

# Brendlər üzrə çatdırılma sayı
st.subheader('🚚 Brendlər üzrə çatdırılma sayı:')
df_delivery = df.groupby("brand")["available_for_delivery"].sum().reset_index().nlargest(10, "available_for_delivery")
fig_delivery = px.bar(df_delivery, x="brand", y="available_for_delivery", labels={"brand":"Brendlər","available_for_delivery": "Çatdırılma sayı"})
st.plotly_chart(fig_delivery)

st.write('>Qrafikdə brendlər üzrə çatdırılma sayı göstərilib. Göründüyü kimi "Jeenmata" və "Coffeemate" üzrə çatdırılma sayı digərlərinə nisbətdə çoxdur.')

# Brendlər üzrə daşınma sayı
st.subheader('📦 Brendlər üzrə daşınma sayı:')
df_pickup = df.groupby("brand")["available_for_pickup"].sum().reset_index().nlargest(10, "available_for_pickup")
fig_pickup = px.bar(df_pickup, x="brand", y="available_for_pickup",  labels={"brand":"Brendlər","available_for_pickup": "Daşınma sayı"})
st.plotly_chart(fig_pickup)

st.write('>Qrafikdə brendlər üzrə daşınma sayı göstərilib. Burda isə birinci yeri "Great Value" brendi ikinci yeri isə "Coffeemate" brendi tutub və burda da say digərlərinə nisbətdə çoxdur.')

# Brendlər üzrə ortalama qiymət
st.subheader('💰 Brendlər üzrə ortalama qiymət:')
df_avg_price = df.groupby("brand")["final_price"].mean().reset_index().nlargest(10, "final_price")
fig_avg_price = px.bar(df_avg_price, x="brand", y="final_price",  labels={"brand":"Brendlər","final_price": "Ortalama Qiymət"})
st.plotly_chart(fig_avg_price)

st.write('>Qrafikdə brendlər üzrə ortalama qiymətin dağılımı göstərilib. Burda isə birinci yeri daşınma sayında olduğu kimi "Great Value" brendi tutub.')

# Brendlər üzrə ortalama endirim məbləği
st.subheader('🎯 Brendlər üzrə ortalama endirim məbləği:')
df_avg_discount = df.groupby("brand")["discount"].mean().reset_index().nlargest(10, "discount")
fig_avg_discount = px.bar(df_avg_discount, x="brand", y="discount",  labels={"brand":"Brendlər","discount": "Ortalama Endirim Məbləği"})
st.plotly_chart(fig_avg_discount)

st.write('>Qrafikdə brendlər üzrə ortalama endirim məbləği göstərilib. Ən çox endirim edilən məhsul "Naclud" məhsuludur, amma bu tam analiz deyil. Əgər məhsul bahalıdırsa o zaman edilən endirim miqdarı da çox olacaq. Buna görə faiz nisbəti ilə baxmaq daha doğru olar.')

# Brendlər üzrə ortalam rating
st.subheader('⭐ Brendlər üzrə ortalam rating:')
df_avg_rating = df.groupby("brand")["rating"].mean().reset_index().nlargest(10, "rating")
fig_avg_rating = px.bar(df_avg_rating, x="brand", y="rating",  labels={"brand":"Brendlər","rating": "Ortalama Rating"})
st.plotly_chart(fig_avg_rating)

st.write('>Qrafikdə brendlər üzrə ortalama ratinq skoru göstərilib. Ən çox ratinq skoru "Bellucci" brendindəddir.')

# --- Kateqoriyalar Üzrə Analiz ---
st.header('📌 Kateqoriyalar Üzrə Analiz')

# Kateqoriyalar üzrə çatdırılma sayı
st.subheader('🚛 Kateqoriyalar üzrə çatdırılma sayı:')
fig_category_delivery = px.bar(df.groupby("category_name")["available_for_delivery"].sum().reset_index().nlargest(10, "available_for_delivery"),
                               x="category_name", y="available_for_delivery", 
                               labels={"category_name":"Kateqoriyalar","available_for_delivery": "Çatdırılma sayı"})
st.plotly_chart(fig_category_delivery)

st.write('>Qrafikdə kateqoriyalar üzrə çatdırılma sayı göstərilib. Göründüyü kimi "Olive Oils" və "Bridal Rings Sets" kateqoriyaları üzrə çatdırılma sayı digərlərinə nisbətdə çoxdur.')

# Kateqoriyalar üzrə daşınma sayı
st.subheader('📦 Kateqoriyalar üzrə daşınma sayı:')
fig_category_pickup = px.bar(df.groupby("category_name")["available_for_pickup"].sum().reset_index().nlargest(10, "available_for_pickup"),
                             x="category_name", y="available_for_pickup", 
                             labels={"category_name":"Kateqoriyalar", "available_for_pickup": "Daşınma sayı"})
st.plotly_chart(fig_category_pickup)

st.write('>Qrafikdə kateqoriyalar üzrə daşınma sayı göstərilib. Burda da birinci yeri "Olive Oils" kateqoriyası tutub və say digərlərinə nisbətdə çoxdur.')

# Kateqoriyalar üzrə ortalama qiymət
st.subheader('💵 Kateqoriyalar üzrə ortalama qiymət:')
fig_category_price = px.bar(df.groupby("category_name")["final_price"].mean().reset_index().nlargest(10, "final_price"),
                            x="category_name", y="final_price", 
                            labels={"category_name":"Kateqoriyalar", "final_price": "Ortalama Qiymət"})
st.plotly_chart(fig_category_price)

st.write('>Qrafikdə kateqoriyalar üzrə ortalama qiymətin dağılımı göstərilib. Burda isə "Cordless Electric Lawn Mowers" tutub.')

# Brendlər üzrə ortalama endirim məbləği
st.subheader('🎯 Kateqoriyalar üzrə ortalama endirim məbləği:')
fig_avg_discount = px.bar(df.groupby("category_name")["discount"].mean().reset_index().nlargest(10, "discount"),
                          x="category_name", y="discount", 
                          labels={"category_name":"Kateqoriyalar", "discount": "Ortalama Endirim Məbləği"})
st.plotly_chart(fig_avg_discount)

st.write('>Qrafikdə kateqoriyalar üzrə ortalama endirim məbləği göstərilib. Ən çox endirim edilən məhsul "All desctop computers" məhsuludur.')

# Brendlər üzrə ortalam rating
st.subheader('⭐ Kateqoriyalar üzrə ortalam rating:')
fig_avg_rating = px.bar(df.groupby("category_name")["rating"].mean().reset_index().nlargest(10, "rating"),
                        x="category_name", y="rating", 
                        labels={"category_name":"Kateqoriyalar", "rating": "Ortalama Rating"})
st.plotly_chart(fig_avg_rating)

st.write('>Qrafikdə kateqoriyalar üzrə ortalama ratinq skoru göstərilib. Ən çox ratinq skoru "Chocolate Powders" kateqoriyasındadır.')


# --- Satıcılar Üzrə Analiz ---
st.header('📌 Satıcılar Üzrə Analiz')

# Satıcılar üzrə sifariş sayı
st.subheader('📊 Satıcılar üzrə sifariş sayı:')
fig_seller_orders = px.bar(df.groupby("seller")["product_id"].count().reset_index().nlargest(10, "product_id"),
                           x="seller", y="product_id", 
                           labels={"seller": "Satıcılar","product_id": "Sifariş Sayı"})
st.plotly_chart(fig_seller_orders)

st.write('>Qrafikdə satıcılar üzrə toplam sifariş sayı göstərilib.')

# Satıcılar üzrə toplam məbləğ
st.subheader('💰 Satıcılar üzrə toplam məbləğ:')
fig_seller_total = px.bar(df.groupby("seller")["final_price"].sum().reset_index().nlargest(10, "final_price"),
                          x="seller", y="final_price", 
                          labels={"seller": "Satıcılar", "final_price": "Toplam Məbləğ"})
st.plotly_chart(fig_seller_total)

st.write('>Burda isə satıcılar üzrə sifarişlərdə ödənilən toplam məbləğ göstərilib.')

# Satıcılar üzrə ortalam rating
st.subheader('⭐ Satıcılar üzrə ortalama rating:')
fig_avg_rating = px.bar(df.groupby("seller")["rating"].mean().reset_index().nlargest(10, "rating"),
                        x="seller", y="rating", 
                        labels={"seller": "Satıcılar", "rating": "Ortalama Rating"})
st.plotly_chart(fig_avg_rating)

st.write('>Burda isə satıcılar üzrə verilən ratinqlər göstərilib.')

# --- Çatdırılma Müddəti Üzrə Analiz ---
st.header('📌 Pulsuz Geri Qaytarma Müddəti Üzrə Analiz')

# Çatdırılma müddəti üzrə sifariş sayı
st.subheader('🛍️ Pulsuz Geri Qaytarma üzrə sifariş sayı:')
fig_free_returns_count = px.bar(df.groupby("free_returns")["product_id"].count().reset_index().nlargest(10, "product_id"),
                                x="free_returns", y="product_id", 
                                labels={"free_returns":"Pulsuz Geri Qaytarma Müddəti","product_id": "Sifariş Sayı"})
st.plotly_chart(fig_free_returns_count)

st.write('>Geri qaytarılma tarixi üzrə sifariş sayı göstərilib. Burda təbii ki insanların hansı məhsula daha çox önəm verdiyi araşdırmaq üçün faiz payı tapılmalıdır. Bəlkə 90% məhsula "Free 90-day returns" təklifi verilir?')

# Çatdırılma müddəti üzrə ortalama ratinq
st.subheader('⭐ Pulsuz Geri Qaytarma üzrə ortalama ratinq:')
fig_free_returns_rating = px.bar(df.groupby("free_returns")["rating"].mean().reset_index().nlargest(10, "rating"),
                                 x="free_returns", y="rating", 
                                 labels={"free_returns":"Pulsuz Geri Qaytarma Müddəti", "rating": "Ortalama Ratinq"})
st.plotly_chart(fig_free_returns_rating)

st.write('>Son olaraq isə, geri qaytarılma tarixi üzrə ortalama ratinq göstərilib. Əslində insanlar qaytarılma tarixi yüksək olan məhsullardan yaxud xidmətlər razı qala bilər. Amma məlumat deyir ki, burda əlaqə o qədər də güclü deyil. Yəni ola bilər ki pis məhsul olsun amma free return olsun bu zaman belə alıcılar narazı qala bilirlər.')


# Footer
st.markdown(
    """
    ---
    <div style="text-align: center;">
        <p><strong>Produced by Riyad Ahmadov</strong></p>
        <p>
            <a href="https://github.com/riyadahmadov" target="_blank">GitHub</a> |
            <a href="https://www.linkedin.com/in/riyadahmadov/" target="_blank">LinkedIn</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ✅Done
