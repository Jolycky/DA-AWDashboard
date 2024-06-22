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
        fig = px.line(budget, x='Year', y='Budget', title='Budget per Year')
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
            Grafik garis menunjukkan total budget per tahun dari dataset yang diberikan.
            - Jika garis bergerak naik, ini menunjukkan total budget film meningkat dari tahun ke tahun.
            - Jika garis bergerak turun, ini menunjukkan total budget film menurun dari tahun ke tahun.
            - Jika garis bergerak datar, ini menunjukkan total budget film stabil dari tahun ke tahun.
            - Puncak garis menunjukkan tahun dengan total budget tertinggi.
            - Ujung garis menunjukkan tahun dengan total budget terendah.
            """)

    with tab2:
        filtered['Short_Name'] = filtered['Name'].apply(lambda x: x if len(x) <= 15 else x[:12] + '...')
        fig = px.bar(filtered, x='Short_Name', y=['Gross_US', 'Gross_World'], barmode='group',
             title='Perbandingan Pendapatan AS & Kanada dengan Pendapatan Global',
             labels={'value': 'Pendapatan', 'variable': 'Kategori', 'Short_Name': 'Film'})

        # Update layout for better visualization
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)
        with st.expander("Analysis", expanded=False):
            st.markdown('**Interpretasi Perbandingan Pendapatan AS & Kanada dengan Pendapatan Global**')
            st.write("""
            Grafik batang menunjukkan perbandingan pendapatan AS & Kanada dengan pendapatan global dari film-film yang dianalisis.
            - Setiap batang mewakili pendapatan AS & Kanada dan pendapatan global dari film yang berbeda.
            - Jika batang pendapatan AS & Kanada lebih tinggi dari batang pendapatan global, ini menunjukkan bahwa film tersebut mendapatkan pendapatan yang lebih tinggi di AS & Kanada daripada secara global.
            - Jika batang pendapatan AS & Kanada lebih rendah dari batang pendapatan global, ini menunjukkan bahwa film tersebut mendapatkan pendapatan yang lebih tinggi secara global daripada di AS & Kanada.
            - Jika batang pendapatan AS & Kanada dan batang pendapatan global sejajar, ini menunjukkan bahwa film tersebut mendapatkan pendapatan yang seimbang di AS & Kanada dan secara global.
            - Grafik ini membantu dalam memahami perbandingan pendapatan AS & Kanada dan pendapatan global dari film-film yang dianalisis.
            """)

def distribution():
    st.header('Distribution Data IMDB')
    tab1, tab2 = st.tabs(['Gross_World', 'Budget'])
    with tab1:
        fig = px.histogram(filtered, x='Gross_World', title='Gross World Distribution', nbins=20, histnorm='percent')
        fig.update_layout(
            xaxis_title='Gross World',
            yaxis_title='Percentage',
            showlegend=False
        )
        fig.update_traces(marker_color='#1f77b4')
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
        fig = px.histogram(filtered, x='Budget', title='Budget Distribution', nbins=20, histnorm='percent')
        fig.update_layout(
            xaxis_title='Budget',
            yaxis_title='Percentage',
            showlegend=False
        )
        fig.update_traces(marker_color='#1f77b4')
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
    tab1, tab2 = st.tabs(['Gross', 'Rating'])
    with tab1:
        filtered['Short_Name'] = filtered['Name'].apply(lambda x: x if len(x) <= 15 else x[:12] + '...')
        fig = px.area(filtered, 
                  x='Short_Name', 
                  y=['Gross_World', 'Gross_US'], 
                  title='Composition of Gross Data',
                  labels={'Gross_World', 'Gross_US'},
                  template='plotly_dark')
    
        fig.update_layout(
            xaxis_title='Film',
            yaxis_title='Pendapatan',
            legend_title=None,
            showlegend=True,
        )

        st.plotly_chart(fig)
        with st.expander("Analysis", expanded=False):
            st.markdown('**Interpretasi Komposisi Gross Data**')
            st.write("""
            Grafik area menunjukkan komposisi pendapatan film dari dataset yang diberikan.
            - Setiap warna mewakili pendapatan global atau pendapatan AS & Kanada dari film yang berbeda.
            - Grafik ini membantu dalam memahami bagaimana pendapatan global dan pendapatan AS & Kanada berubah sepanjang waktu.
            """)
    with tab2:
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
    fig = px.scatter(
        filtered, 
        x='Budget', 
        y='Gross_World', 
        color='Durasi(Menit)', 
        size='Durasi(Menit)', 
        hover_data=['Name', 'Year'],
        labels={'Budget': 'Anggaran (Budget)', 'Gross_World': 'Pendapatan Global (Gross World)', 'Durasi(Menit)': 'Durasi Film (Menit)'},
        title='Budget vs Gross World vs Durasi Film')
    st.plotly_chart(fig)

def show_imdb():
    st.title('IMDB Data Visualization Dashboard')
    filter_data()
    home()
    composition()
    relationship()
    comparison()
    distribution()