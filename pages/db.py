from sqlalchemy import create_engine
import pymysql
import pandas as pd
import streamlit as st
import plotly.express as px
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

def filter_data():
    st.sidebar.header('Filter Data Adventure Works:')
    region = st.sidebar.multiselect("Pilih Wilayah", options = df["SalesTerritoryCountry"].unique(), default = df["SalesTerritoryCountry"].unique())
    min_year = st.sidebar.selectbox('Min Year', options=[None] + list(df['Year'].sort_values(ascending=True).unique()), index=0)
    max_year = st.sidebar.selectbox('Max Year', options=[None] + list(df['Year'].sort_values(ascending=False).unique()), index=0)

    global filtered
    filtered = df.copy()
    filtered = filtered[filtered['SalesTerritoryCountry'].isin(region)]
    if min_year is not None:
        filtered = filtered[filtered['Year'] >= min_year]
    if max_year is not None:
        filtered = filtered[filtered['Year'] <= max_year]
    st.divider()
    return filtered

def comparison():
    tab1, tab2 = st.columns(2)
    with tab1:
        sales = filtered.groupby('Year')['SalesAmount'].sum().reset_index()
        fig = px.bar(sales, x='Year', y='SalesAmount', title='Sales Amount per Year')
        st.plotly_chart(fig)
    with tab2:
        quantity = filtered.groupby('Year')['OrderQuantity'].sum().reset_index()
        fig = px.bar(quantity, x='Year', y='OrderQuantity', title='Order Quantity per Year')
        st.plotly_chart(fig)

def distribution():
    tab1, tab2 = st.columns(2)
    with tab1:
        fig = px.histogram(filtered, x='SalesAmount', title='Sales Amount Distribution')
        st.plotly_chart(fig)
    with tab2:
        fig = px.histogram(filtered, x='OrderQuantity', title='Order Quantity Distribution')
        st.plotly_chart(fig)

def composition():
    category = filtered.groupby('EnglishProductCategoryName').agg({
        'EnglishProductCategoryName': 'count'
    })
    category = category.rename(columns={'EnglishProductCategoryName': 'Total'}).reset_index()
    fig = px.pie(category, values='Total', names='EnglishProductCategoryName', title='Product Category Composition')
    st.plotly_chart(fig)

def relationship():
    tab1, tab2 = st.columns(2)
    with tab1:
        sales_quantity = filtered[['SalesAmount', 'OrderQuantity']]
        fig = px.scatter(sales_quantity, x='SalesAmount', y='OrderQuantity', title='Sales Amount vs Order Quantity')
        max_quantity = sales_quantity['OrderQuantity'].idxmax()
        min_quantity = sales_quantity['OrderQuantity'].idxmin()
        fig.add_annotation(x=sales_quantity.loc[max_quantity, 'SalesAmount'], y=sales_quantity.loc[max_quantity, 'OrderQuantity'], text="Max")
        fig.add_annotation(x=sales_quantity.loc[min_quantity, 'SalesAmount'], y=sales_quantity.loc[min_quantity, 'OrderQuantity'], text="Min")
        st.plotly_chart(fig)
    with tab2:
        category_sales = filtered[['EnglishProductCategoryName', 'SalesAmount']]
        fig = px.scatter(category_sales, x='SalesAmount', y='EnglishProductCategoryName', title='Sales Amount per Product Category')
        st.plotly_chart(fig)

def show_db():
    st.title('Adventure Works Data Visualization Dashboard')
    filter_data()
    home()
    comparison()
    distribution()
    composition()
    relationship()

