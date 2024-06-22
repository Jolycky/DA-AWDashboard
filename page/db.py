from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection details
DB_HOST = st.secrets['DB_HOST']
DB_PORT = 3306
DB_DATABASE = st.secrets['DB_DATABASE']
DB_USER = st.secrets['DB_USER']
DB_PASS = st.secrets['DB_PASS']

# Create the database connection string
db_url = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

# Create the engine
engine = create_engine(db_url)

# Test the connection
try:
    with engine.connect() as connection:
        print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {str(e)}")

# Query the database using SQLAlchemy
query = """
SELECT
    fis.SalesOrderNumber,
    YEAR(fis.OrderDate) AS 'Year',
    MONTHNAME(fis.OrderDate) AS 'Month',
    fis.SalesAmount,
    fis.OrderQuantity,
    fis.TotalProductCost,
    CONCAT(dc.FirstName, ' ', dc.LastName) AS 'Customer',
    dc.Gender,
    dc.YearlyIncome,
    dst.SalesTerritoryCountry,
    dpc.EnglishProductCategoryName
FROM factinternetsales fis
LEFT JOIN dimsalesterritory dst 
    ON fis.SalesTerritoryKey = dst.SalesTerritoryKey
LEFT JOIN dimcustomer dc
    ON fis.CustomerKey = dc.CustomerKey
LEFT JOIN dimproduct dp
    ON fis.ProductKey = dp.ProductKey
LEFT JOIN dimproductsubcategory dps
    ON dp.ProductSubcategoryKey = dps.ProductSubcategoryKey
LEFT JOIN dimproductcategory dpc
    ON dps.ProductCategoryKey = dpc.ProductCategoryKey;
"""
df = pd.read_sql(query, engine)

def home():
    with st.expander("Table Data Adventure Works"):
        showData = st.multiselect('Filter Kolom: ', df.columns, default=df.columns.tolist())
        st.write(df[showData])

def filter_df(df, year_list=None, country_list=None, gender_list=None, category_list=None):
    query_str = " & ".join([
        f"Year == {year_list}" if year_list is not None else '',
        f"SalesTerritoryCountry == {country_list}" if country_list is not None else '',
        f"Gender == {gender_list}" if gender_list is not None else '',
        f"EnglishProductCategoryName == {category_list}" if category_list is not None else ''
    ]).strip(' & ')
    
    return df.query(query_str)

def show_db():
    st.title('Adventure Works Data Visualization Dashboard')
    home()

    years = df["Year"].unique().tolist()
    countries = df["SalesTerritoryCountry"].unique().tolist()

    # ---- SIDEBAR ----
    st.sidebar.header("Filtering")

    year = st.sidebar.multiselect(
        "Select the year",
        options=years,
        default=years
    )

    country = st.sidebar.multiselect(
        "Select the country",
        options=countries,
        default=countries
    )

    # Menentukan nilai default jika tidak ada pilihan
    if year:
        year_list = year
    else:
        year_list = years

    if country:
        country_list = country
    else:
        country_list = countries

    df_selection = filter_df(df, year_list, country_list)

    # TOP KPI's
    total_sales = df_selection["SalesAmount"].count()
    total_sales_amount = df_selection["SalesAmount"].sum()
    average_sales = df_selection["SalesAmount"].mean()
    top_category = df_selection["EnglishProductCategoryName"].mode()

    # Define the CSS for the custom styling
    st.markdown("""
        <style>
            .dashboard-box {
                border: 2px solid white;
                padding: 15px; /* Adjusted padding */
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                text-align: center;
                height: 180px; /* Adjusted height */
                display: flex;
                flex-direction: column;
                justify-content: center;
                color: white;
            }
            .dashboard-box p {
                font-family: 'Arial', sans-serif;
                font-size: 14px;
                margin: 5px 0;
            }
            .dashboard-box p.title {
                font-size: 17px;
                font-weight: bold;
            }
            .dashboard-box p.logo {
                font-size: 40px;
                margin: 0;
            }
            .box1 {
                background-color: #1f77b4; /* Blue */
            }
            .box2 {
                background-color: #ff7f0e; /* Orange */
            }
            .box3 {
                background-color: #2ca02c; /* Green */
            }
            .box4 {
                background-color: #d62728; /* Red */
            }
        </style>
    """, unsafe_allow_html=True)

    # Create the dashboard layout with columns
    left_column, middle_column1, middle_column2, right_column = st.columns(4)

    with left_column:
        text = f'''
        <div class="dashboard-box box1">
            <p class="logo">📖</p>
            <p class="title">Total Sales: </p>
            <p>{total_sales}</p>
        </div>
        '''
        st.markdown(text, unsafe_allow_html=True)

    with middle_column1:
        text = f'''
        <div class="dashboard-box box2">
            <p class="logo">💰</p>
            <p class="title">Total Sales Amount: </p>
            <p>US ${total_sales_amount:,.2f}</p>
        </div>
        '''
        st.markdown(text, unsafe_allow_html=True)

    with middle_column2:
        text = f'''
        <div class="dashboard-box box3">
            <p class="logo">💵</p>
            <p class="title">Average Sales Amount: </p>
            <p>US ${average_sales:,.2f}</p>
        </div>
        '''
        st.markdown(text, unsafe_allow_html=True)

    with right_column:
        text = f'''
        <div class="dashboard-box box4">
            <p class="logo">🏆</p>
            <p class="title">Top Category: </p>
            <p>{top_category[0]}</p>
        </div>
        '''
        st.markdown(text, unsafe_allow_html=True)

    # ---- TOTAL SALES AMOUNT vs TOTAL COST BY COUNTRY ----
    chart1 = df_selection.groupby("SalesTerritoryCountry").sum()[["SalesAmount", "TotalProductCost"]]

    # Membuat column histogram dengan Plotly Express
    fig_chart1 = px.histogram(
        chart1,
        x=chart1.index,
        y=["SalesAmount", "TotalProductCost"],
        title="<b>TOTAL SALES AMOUNT vs TOTAL COST BY COUNTRY</b>",
        template="plotly_dark",
        barmode="group",
        color_discrete_sequence=["#FFD184", "#E2AA00"],
        text_auto="$.2s"
    )

    # Mengupdate layout chart untuk tampilan yang lebih menarik
    fig_chart1.update_layout(
        autosize=True,
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        yaxis_title=None,
        xaxis_title=None,
        yaxis={'visible': True, 'showticklabels': True, 'title_text': 'Amount'},
        xaxis=dict(tickfont=dict(size=14), title_text='Country'),
        legend=dict(orientation='h', yanchor='bottom', xanchor='center', x=0.5, y=1.02, title=None, font=dict(size=15)),
        title={'x': 0.5, 'xanchor': 'center'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    fig_chart1.update_traces(
        textposition="outside",
        marker_line_color='#00172B',
        marker_line_width=2,
        opacity=0.9,
        hovertemplate='Country: %{x}<br>Amount: %{y}',
    )

    # ---- TOTAL OF SALES BY MONTH ----
    chart2 = df_selection.groupby("Month", as_index=False).sum()[["Month", "OrderQuantity"]]
    chart2["Month"] = pd.Categorical(chart2["Month"], ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    chart2.sort_values("Month", inplace=True, ascending=False)

    # Custom color palette with three different shades of red
    custom_red_palette = ["#FFF5E0", "#FF6969", "#C70039"]  # Pure Red, Tomato, OrangeRed

    # Assigning the custom color palette to the months
    color_mapping = {month: custom_red_palette[i % len(custom_red_palette)] for i, month in enumerate(chart2["Month"])}

    # Create a horizontal bar chart with Plotly Express
    fig_chart2 = px.bar(
        chart2,
        x="OrderQuantity",
        y="Month",
        title="<b>TOTAL SALES BY MONTH</b>",
        template="plotly_dark",  # Using a dark template for a modern look
        orientation="h",
        text_auto=True
    )

    # Update the bar colors based on the custom palette
    fig_chart2.update_traces(marker_color=[color_mapping[month] for month in chart2["Month"]])

    # Update chart layout for a more attractive appearance
    fig_chart2.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        yaxis_title=None,
        xaxis_title='Order Quantity',
        xaxis=dict(tickfont=dict(size=14), title_font=dict(size=16)),
        yaxis=dict(tickfont=dict(size=14), title_font=dict(size=16)),
        height=800,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
        showlegend=False
    )

    # Update trace settings to enhance chart appearance
    fig_chart2.update_traces(
        textposition="inside",
        marker_line_color='#FFFFFF',  # White outline for better contrast
        marker_line_width=1.5,
        opacity=0.9,
        hovertemplate='<b>Month:</b> %{y}<br><b>Order Quantity:</b> %{x}'  # More informative hover template
    )

    # ---- SALES BY CATEGORY ----
    chart3 = df_selection.groupby("EnglishProductCategoryName").sum()[["OrderQuantity"]]

    # Membuat pie chart dengan Plotly Express
    fig_chart3 = px.pie(
        chart3,
        values="OrderQuantity",
        title="<b>SALES BY CATEGORY</b>",
        names=chart3.index,
        color_discrete_sequence=["#4472C4", "#5B9BD5", "#A5A5A5"]
    )

    # Mengupdate layout chart untuk tampilan yang lebih menarik
    fig_chart3.update_layout(
        uniformtext_minsize=14,
        uniformtext_mode='hide',
        height=400,  # Sesuaikan tinggi chart
        title={'x': 0.5, 'xanchor': 'center'},
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            xanchor='center',
            x=0.5,  # Menempatkan legenda di tengah bawah grafik
            y=-0.2,  # Mengatur posisi legenda sedikit di bawah grafik
            font=dict(size=12)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Mengupdate tampilan trace untuk membuat chart lebih menarik
    fig_chart3.update_traces(
        hoverinfo='label+percent',
        textinfo='percent',  # Menampilkan hanya persentase di dalam pie chart
        textfont_size=16,
        marker=dict(line=dict(color="#00172B", width=2)),
        pull=[0.1, 0, 0],  # Menarik slice pertama untuk menekankan
        rotation=45,  # Memutar pie chart untuk sudut yang berbeda
        hole=0.4  # Mengubah pie chart menjadi doughnut chart
    )

    # ---- SALES BY GENDER ----
    chart4 = df_selection.groupby("Gender").sum()[["OrderQuantity"]]

    # Create a pie chart with Plotly Express
    fig_chart4 = px.pie(
        chart4,
        values="OrderQuantity",
        names=chart4.index,
        title="<b>Sales by Gender</b>",
        hole=0.45,
        color_discrete_map={
            'Male': '#365E32',  # Dark Green
            'Female': '#81A263'  # Light Green
        }
    )

    # Update chart layout for a more attractive appearance
    fig_chart4.update_layout(
        uniformtext_minsize=14,
        uniformtext_mode='hide',
        height=300,
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
        margin=dict(t=80, b=0, l=0, r=0),
        showlegend=False
    )

    # Update trace settings to enhance chart appearance
    fig_chart4.update_traces(
        insidetextfont={'color': 'white'},
        hoverinfo='label+percent',
        textinfo='percent+label',
        marker=dict(line=dict(color="white", width=2)),
    )

    # Bubble plot SalesMouth vs EnglishPromotionName
    chart5 = df_selection.groupby('Customer').agg({'SalesAmount': 'sum','YearlyIncome': 'mean',}).reset_index()
    
    min_val = chart5['SalesAmount'].min()
    max_val = chart5['SalesAmount'].max()

    chart5['color'] = 'mid'
    chart5.loc[chart5['SalesAmount'] == min_val, 'color'] = 'min'
    chart5.loc[chart5['SalesAmount'] == max_val, 'color'] = 'max'

    fig_chart5 = px.scatter(
        chart5,
        x='YearlyIncome',
        y='SalesAmount',
        color='color',
        size='SalesAmount',
        title="<b>Yearly Income vs Sales Amount</b>",
        template='plotly_dark',
        labels={'YearlyIncome': 'Yearly Income', 'SalesAmount': 'Sales Amount'},
        color_discrete_map={'min': '#1f77b4', 'mid': '#ff7f0e', 'max': '#d62728'},
        size_max=50,
        hover_data={'Customer': True},
        width=800,
        height=600
    )

    fig_chart5.update_layout(
        xaxis_title='Yearly Income',
        yaxis_title='Sales Amount',
        title={'x': 0.5, 'xanchor': 'center'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    fig_chart5.update_traces(
        hovertemplate='<b>Yearly Income:</b> %{x}<br><b>Sales Amount:</b> %{y}<br'
    )

    # ---- PLACING CHARTS ON MAIN PAGE ----
    st.plotly_chart(fig_chart1, use_container_width=True)
    with st.expander("Analisis Total Sales Amount vs Total Cost by Country", expanded=False):
        # Analisis tambahan
        total_sales = chart1['SalesAmount'].sum()
        total_cost = chart1['TotalProductCost'].sum()
        avg_sales = chart1['SalesAmount'].mean()
        avg_cost = chart1['TotalProductCost'].mean()
        max_sales_country = chart1['SalesAmount'].idxmax()
        min_sales_country = chart1['SalesAmount'].idxmin()
        max_cost_country = chart1['TotalProductCost'].idxmax()
        min_cost_country = chart1['TotalProductCost'].idxmin()

        st.write(f"Total penjualan adalah {total_sales}.")
        st.write(f"Total biaya produk adalah {total_cost}.")
        st.write(f"Rata-rata penjualan adalah {avg_sales}.")
        st.write(f"Rata-rata biaya produk adalah {avg_cost}.")
        st.write(f"Negara dengan penjualan tertinggi adalah {max_sales_country} dengan {chart1.loc[max_sales_country, 'SalesAmount']}.")
        st.write(f"Negara dengan penjualan terendah adalah {min_sales_country} dengan {chart1.loc[min_sales_country, 'SalesAmount']}.")
        st.write(f"Negara dengan biaya produk tertinggi adalah {max_cost_country} dengan {chart1.loc[max_cost_country, 'TotalProductCost']}.")
        st.write(f"Negara dengan biaya produk terendah adalah {min_cost_country} dengan {chart1.loc[min_cost_country, 'TotalProductCost']}.")
        st.markdown("")

        # Interpretasi
        st.markdown('**Interpretasi Histogram Total Sales Amount vs Total Cost by Country**')
        st.write("""
        Grafik histogram ini menunjukkan perbandingan antara jumlah total penjualan dan total biaya produk berdasarkan negara.
        - Puncak histogram mewakili negara dengan jumlah total penjualan atau biaya produk tertentu yang paling sering muncul dalam dataset.
        - Jika satu negara memiliki nilai SalesAmount dan TotalProductCost yang tinggi, ini menunjukkan negara tersebut memiliki kontribusi signifikan dalam penjualan dan biaya produk.
        - Jika SalesAmount lebih tinggi daripada TotalProductCost secara signifikan di satu negara, ini menunjukkan margin keuntungan yang lebih besar di negara tersebut.
        - Rentang nilai menunjukkan variasi penjualan dan biaya produk di berbagai negara.
        - Simetri histogram menunjukkan distribusi penjualan dan biaya produk yang seimbang atau tidak di berbagai negara.
        """)
    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(fig_chart3, use_container_width=True)
        with st.expander("Analysis", expanded=False):
            # Interpretasi
                st.markdown('**Interpretasi Sales by Category**')
                st.write("""
                Grafik pie chart menunjukkan distribusi penjualan berdasarkan kategori produk. Beberapa poin penting dari grafik ini adalah:
                - **Persentase Penjualan:** Grafik menunjukkan persentase kontribusi dari setiap kategori produk terhadap total penjualan. 
                - **Kategori dengan Penjualan Tertinggi:** Slice yang paling besar menunjukkan kategori dengan jumlah penjualan tertinggi. Misalnya, jika kategori 'Electronics' memiliki slice terbesar, itu berarti 'Electronics' memiliki penjualan tertinggi.
                - **Kategori dengan Penjualan Terendah:** Slice yang paling kecil menunjukkan kategori dengan jumlah penjualan terendah.
                - **Penekanan Kategori:** Slice pertama ditarik keluar untuk menekankan kategori dengan penjualan tertinggi. Hal ini membantu penonton untuk dengan cepat mengidentifikasi kategori utama.
                - **Distribusi Warna:** Warna yang berbeda digunakan untuk setiap kategori untuk memudahkan identifikasi visual.

                Grafik ini membantu dalam memahami bagaimana penjualan didistribusikan di antara berbagai kategori produk, dan memungkinkan untuk mengidentifikasi kategori yang berkinerja baik dan yang mungkin memerlukan perhatian lebih.
                """)
        st.plotly_chart(fig_chart4, use_container_width=True)
        with st.expander("Analysis", expanded=False):
            # Interpretasi
            total_orders = chart4["OrderQuantity"].sum()
            male_orders = chart4.loc["M", "OrderQuantity"]
            female_orders = chart4.loc["F", "OrderQuantity"]
            male_percentage = (male_orders / total_orders) * 100
            female_percentage = (female_orders / total_orders) * 100

            st.markdown('**Interpretasi Sales by Gender**')
            st.write(f"Total penjualan yang dianalisis adalah {total_orders} pesanan.")
            st.write(f"Jumlah pesanan dari pelanggan pria adalah {male_orders} ({male_percentage:.2f}%).")
            st.write(f"Jumlah pesanan dari pelanggan wanita adalah {female_orders} ({female_percentage:.2f}%).")
            st.write("""
            - Diagram pie menunjukkan distribusi pesanan berdasarkan jenis kelamin.
            - Warna hijau tua mewakili pesanan dari pria, dan warna hijau muda mewakili pesanan dari wanita.
            - Jika salah satu segmen jauh lebih besar daripada yang lain, itu menunjukkan bahwa satu jenis kelamin berkontribusi lebih banyak terhadap total pesanan.
            - Proporsi pesanan antara pria dan wanita dapat memberikan wawasan tentang preferensi atau kebiasaan pembelian di antara kelompok pelanggan yang berbeda.
            """)

    with right_column:
        st.plotly_chart(fig_chart2, use_container_width=True)
        with st.expander("Analysis", expanded=False):
            # Analisis dan interpretasi
            st.markdown('**Interpretasi dari Grafik Total Sales by Month**')
            st.write("""
            Grafik ini menunjukkan distribusi total penjualan berdasarkan bulan sepanjang tahun.

            **Analisis Kuantitatif:**
            - **Total Order Quantity:** Jumlah total pesanan dalam dataset.
            - **Bulan dengan Penjualan Tertinggi:** Bulan dengan jumlah pesanan tertinggi.
            - **Bulan dengan Penjualan Terendah:** Bulan dengan jumlah pesanan terendah.
            - **Rata-rata Order Quantity per Bulan:** Rata-rata jumlah pesanan per bulan.
            - **Variasi Penjualan per Bulan:** Apakah ada perbedaan yang signifikan antara bulan-bulan dengan penjualan tertinggi dan terendah.

            **Interpretasi:**
            - **Musiman Penjualan:** Bulan-bulan dengan puncak penjualan yang tinggi dapat menunjukkan tren musiman atau promosi khusus.
            - **Perencanaan dan Strategi:** Informasi ini dapat digunakan untuk merencanakan stok dan strategi pemasaran di bulan-bulan tertentu.
            - **Efektivitas Promosi:** Bulan dengan lonjakan penjualan dapat menunjukkan efektivitas kampanye promosi atau peluncuran produk baru.
            - **Ketersediaan Produk:** Bulan dengan penjualan rendah mungkin membutuhkan analisis lebih lanjut untuk memastikan ketersediaan produk atau menangani faktor-faktor lain yang mempengaruhi penjualan.
            """)
    st.plotly_chart(fig_chart5, use_container_width=True)
    with st.expander("Analysis", expanded=False):
        st.markdown('**Interpretasi Yearly Income vs Sales Amount**')
        st.write("""
        Grafik scatter plot menunjukkan hubungan antara pendapatan tahunan (Yearly Income) dan jumlah penjualan (Sales Amount) untuk setiap pelanggan.
        - **Poin Data:** Setiap titik dalam grafik mewakili satu pelanggan, dengan ukuran titik menunjukkan jumlah penjualan.
        - **Warna:** 
            - **min (Biru):** Pelanggan dengan jumlah penjualan terendah.
            - **mid (Oranye):** Pelanggan dengan jumlah penjualan di antara yang terendah dan tertinggi.
            - **max (Merah):** Pelanggan dengan jumlah penjualan tertinggi.
        - **Analisis Data:**
            - **Pendapatan Tahunan vs Jumlah Penjualan:** Grafik ini membantu mengidentifikasi apakah ada korelasi antara pendapatan tahunan pelanggan dan jumlah penjualan.
            - **Pelanggan dengan Pendapatan Tinggi:** Jika pelanggan dengan pendapatan tinggi cenderung memiliki jumlah penjualan yang tinggi, ini mungkin menunjukkan bahwa pendapatan tahunan pelanggan adalah indikator yang baik untuk penjualan.
            - **Outliers:** Perhatikan apakah ada outliers, yaitu pelanggan dengan pendapatan sangat tinggi atau sangat rendah tetapi memiliki jumlah penjualan yang tidak sesuai dengan tren umum.
        - **Rentang Data:**
            - **Pendapatan Tahunan:** Rentang pendapatan tahunan pelanggan di dataset.
            - **Jumlah Penjualan:** Rentang jumlah penjualan dari yang terendah hingga tertinggi.
        """)