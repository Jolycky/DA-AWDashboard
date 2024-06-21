import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("./data/imdb_combined.csv")
df["Year"] = df["Year"].astype(int)

df_selection = df[['Name','Year','Durasi(Menit)','Rating','Budget','Gross_US','Opening_Week','Open_Week_Date','Gross_World','Color','Sound_Mix','Aspect_Ratio']]
# Fungsi Home untuk menampilkan data
def home():
    with st.expander("Table Data IMDB"):
        showData = st.multiselect('Filter Kolom: ', df_selection.columns, default=df_selection.columns.tolist())
        st.write(df_selection[showData])

def filter_data():
    st.sidebar.header('Filter Data')
    min_year = st.sidebar.selectbox('Min Year', options=[None] + list(df['Year'].sort_values(ascending=True).unique()), index=0)
    max_year = st.sidebar.selectbox('Max Year', options=[None] + list(df['Year'].sort_values(ascending=False).unique()), index=0)
    rating_data = st.sidebar.multiselect("Pilih Rating:", options = df["Rating"].unique(),default = df["Rating"].unique())

    global filtered
    filtered = df.copy()
    if min_year is not None:
        filtered = filtered[filtered['Year'] >= min_year]
    if max_year is not None:
        filtered = filtered[filtered['Year'] <= max_year]
    filtered = filtered[filtered['Rating'].isin(rating_data)]
    st.divider()
    return filtered

def comparison():
    st.header('Comparison Data IMDB')
    tab1, tab2 = st.tabs(['Budget', 'Durasi(Menit)'])
    with tab1:
        budget = filtered.groupby('Year')['Budget'].sum().reset_index()
        fig = px.bar(budget, x='Year', y='Budget', title='Budget per Year')
        st.plotly_chart(fig)
        with st.expander("Analysis", expanded=False):
            total_budget = budget['Budget'].sum()
            avg_budget = budget['Budget'].mean()
            max_budget_year = budget.loc[budget['Budget'].idxmax(), 'Year']
            min_budget_year = budget.loc[budget['Budget'].idxmin(), 'Year']
            
            st.markdown('**Analisis Budget**')
            st.write(f"Total budget dari semua tahun adalah {total_budget}.")
            st.write(f"Rata-rata budget per tahun adalah {avg_budget}.")
            st.write(f"Tahun dengan budget tertinggi adalah **{max_budget_year}**.")
            st.write(f"Tahun dengan budget terendah adalah **{min_budget_year}**.")

            # Interpretasi
            st.markdown('**Interpretasi Budget per Year**')
            st.write("""
            Grafik batang menunjukkan distribusi budget per tahun dari dataset yang diberikan.
            - **Total Budget:** Total budget dari semua tahun memberikan gambaran umum mengenai total pengeluaran dalam periode waktu tertentu.
            - **Rata-rata Budget:** Rata-rata budget per tahun menunjukkan tren pengeluaran tahunan.
            - **Tahun dengan Budget Tertinggi dan Terendah:** Menunjukkan tahun dengan pengeluaran terbesar dan terkecil, yang dapat membantu mengidentifikasi pola atau anomali dalam pengeluaran.
            """)
    with tab2:
        durasi = filtered.groupby('Rating')['Durasi(Menit)'].mean().reset_index()
        fig = px.bar(durasi, x='Rating', y='Durasi(Menit)', title='Avarage Durasi(Menit) per Rating')
        st.plotly_chart(fig)
        with st.expander("Analysis", expanded=False):
            avg_durasi = durasi['Durasi(Menit)'].mean()
            max_durasi_rating = durasi.loc[durasi['Durasi(Menit)'].idxmax(), 'Rating']
            min_durasi_rating = durasi.loc[durasi['Durasi(Menit)'].idxmin(), 'Rating']
            
            st.markdown('**Analisis Durasi(Menit)**')
            st.write(f"Rata-rata durasi dari semua rating adalah {avg_durasi} menit.")
            st.write(f"Rating dengan durasi tertinggi adalah **{max_durasi_rating}** dengan rata-rata durasi {durasi.loc[durasi['Durasi(Menit)'].idxmax(), 'Durasi(Menit)']} menit.")
            st.write(f"Rating dengan durasi terendah adalah **{min_durasi_rating}** dengan rata-rata durasi {durasi.loc[durasi['Durasi(Menit)'].idxmin(), 'Durasi(Menit)']} menit.")

            # Interpretasi
            st.markdown('**Interpretasi Average Durasi(Menit) per Rating**')
            st.write("""
            Grafik batang menunjukkan rata-rata durasi (menit) per rating dari dataset yang diberikan.
            - **Rata-rata Durasi:** Menunjukkan berapa lama rata-rata durasi film berdasarkan ratingnya.
            - **Rating dengan Durasi Tertinggi dan Terendah:** Mengidentifikasi rating yang memiliki durasi rata-rata tertinggi dan terendah, yang dapat memberikan wawasan tentang durasi film yang berkaitan dengan rating tertentu.
            """)
def distribution():
    st.header('Distribution Data IMDB')
    tab1, tab2 = st.tabs(['Gross_World', 'Budget'])
    with tab1:
        fig = px.histogram(filtered, x='Gross_World', title='Gross World Distribution')
        st.plotly_chart(fig)
        with st.expander("Analysis", expanded=False):
            total_gross = filtered['Gross_World'].sum()
            avg_gross = filtered['Gross_World'].mean()
            max_gross = filtered['Gross_World'].max()
            min_gross = filtered['Gross_World'].min()
            gross_range = max_gross - min_gross
            
            st.markdown('**Analisis Gross World**')
            st.write(f"Total gross world adalah {total_gross}.")
            st.write(f"Rata-rata gross world adalah {avg_gross}.")
            st.write(f"Gross world tertinggi adalah {max_gross}.")
            st.write(f"Gross world terendah adalah {min_gross}.")
            st.write(f"Rentang gross world adalah {gross_range}.")
            
            # Interpretasi
            st.markdown('**Interpretasi Gross World Distribution**')
            st.write("""
            Grafik histogram menunjukkan distribusi total pendapatan global dari dataset yang diberikan. 
            - Puncak histogram menunjukkan jumlah film dengan pendapatan global tertentu yang paling sering muncul dalam dataset.
            - Jika sebagian besar nilai Gross World berada di ujung kanan histogram, ini menunjukkan beberapa film memiliki pendapatan global yang sangat tinggi, sementara sebagian besar lainnya memiliki pendapatan yang lebih rendah.
            - Rentang yang luas dengan beberapa outliers di ujung kanan menunjukkan variasi yang tinggi dalam pendapatan global.
            - Simetri histogram menunjukkan distribusi pendapatan global yang seimbang atau tidak.
            """)
    with tab2:
        fig = px.histogram(filtered, x='Budget', title='Budget Distribution')
        st.plotly_chart(fig)
        with st.expander("Analysis", expanded=False):
            total_budget = filtered['Budget'].sum()
            avg_budget = filtered['Budget'].mean()
            max_budget = filtered['Budget'].max()
            min_budget = filtered['Budget'].min()

            st.markdown('**Analisis Budget**')
            st.write(f"Total budget adalah {total_budget}.")
            st.write(f"Rata-rata budget adalah {avg_budget}.")
            st.write(f"Budget tertinggi adalah {max_budget}.")
            st.write(f"Budget terendah adalah {min_budget}.")

            # Interpretasi
            st.markdown('**Interpretasi Budget Distribution**')
            st.write("""
            Grafik histogram menunjukkan distribusi total budget dari dataset yang diberikan.
            - Puncak histogram menunjukkan jumlah film dengan budget tertentu yang paling sering muncul dalam dataset.
            - Jika sebagian besar nilai Budget berada di ujung kanan histogram, ini menunjukkan beberapa film memiliki budget yang sangat tinggi, sementara sebagian besar lainnya memiliki budget yang lebih rendah.
            - Rentang yang luas dengan beberapa outliers di ujung kanan menunjukkan variasi yang tinggi dalam budget.
            - Simetri histogram menunjukkan distribusi budget yang seimbang atau tidak.
            """)

def composition():
    st.header('Composition Data IMDB')
    rating = filtered.groupby('Rating').agg({
        'Rating': 'count'
    })
    rating = rating.rename(columns={'Rating': 'Total'}).reset_index()
    fig = px.pie(rating, values='Total', names='Rating', title='Rating Composition')
    st.plotly_chart(fig)
    with st.expander("Analysis", expanded=False):
        st.markdown('**Interpretasi Rating Composition**')
        st.write("""
        Grafik pie menunjukkan komposisi jumlah film berdasarkan rating yang ada di dataset.
        - Setiap irisan pie mewakili proporsi dari jumlah film dengan rating tertentu.
        - Grafik ini membantu dalam memahami distribusi dan dominasi rating tertentu di antara film-film yang dianalisis.
        """)

def relationship():
    st.header('Relationship Data IMDB')
    tab1, tab2 = st.tabs(['Budget vs Gross_World', 'Rating vs Budget'])
    with tab1:
        budget_gross = filtered[['Budget', 'Gross_World']]
        fig = px.scatter(budget_gross, x='Budget', y='Gross_World', title='Budget vs Gross')
        max_gross = budget_gross['Gross_World'].idxmax()
        min_gross = budget_gross['Gross_World'].idxmin()
        fig.add_annotation(x=budget_gross.loc[max_gross, 'Budget'], y=budget_gross.loc[max_gross, 'Gross_World'], text="Max")
        fig.add_annotation(x=budget_gross.loc[min_gross, 'Budget'], y=budget_gross.loc[min_gross, 'Gross_World'], text="Min")
        st.plotly_chart(fig)
        with st.expander("Analysis", expanded=False):
            correlation = budget_gross['Budget'].corr(budget_gross['Gross_World'])
            st.markdown('**Analisis Budget vs Gross World**')
            st.write(f"Korelasi antara budget dan gross world adalah {correlation}.")
            
            # Interpretasi
            st.markdown('**Interpretasi Budget vs Gross World**')
            st.write("""
            Grafik scatter menunjukkan hubungan antara budget dan gross world dari dataset yang diberikan.
            - Korelasi positif menunjukkan bahwa semakin tinggi budget, semakin tinggi pula gross world film.
            - Korelasi negatif menunjukkan bahwa semakin tinggi budget, semakin rendah gross world film.
            - Korelasi nol menunjukkan tidak ada hubungan antara budget dan gross world film.
            - Penambahan anotasi pada titik data tertinggi dan terendah membantu mengidentifikasi film dengan budget dan gross world tertinggi dan terendah.
            """)

    with tab2:
        rating_budget = filtered[['Rating', 'Budget']]
        fig = px.scatter(rating_budget, x='Budget', y='Rating', title='Rating vs Budget')
        max_budget = rating_budget['Budget'].idxmax()
        min_budget = rating_budget['Budget'].idxmin()
        fig.add_annotation(x=rating_budget.loc[max_budget, 'Budget'], y=rating_budget.loc[max_budget, 'Rating'], text="Max")
        fig.add_annotation(x=rating_budget.loc[min_budget, 'Budget'], y=rating_budget.loc[min_budget, 'Rating'], text="Min")
        st.plotly_chart(fig)

def show_imdb():
    st.title('IMDB Data Visualization Dashboard')
    filter_data()
    home()
    distribution()
    composition()
    relationship()
    comparison()