from sqlalchemy import create_engine
import pymysql
import pandas as pd
import streamlit as st
import pandas as pd
import sqlalchemy as db
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

#try query the database using sqlalchemy
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
print(df.head(5))

# ---- FILTER OPTIONS ----

years = df["Year"].unique().tolist()
countries = df["SalesTerritoryCountry"].unique().tolist()
genders = df["Gender"].unique().tolist()
categories = df["EnglishProductCategoryName"].unique().tolist()

# ----


# ---- SIDEBAR ----
st.sidebar.header("Filtering")

year = st.sidebar.multiselect(
    "Select the year",
    options=years,
    default=years)

country = st.sidebar.multiselect(
    "Select the country",
    options=countries,
    default=countries)

gender = st.sidebar.multiselect(
    "Select the customer gender",
    options=genders,
    default=genders)

category = st.sidebar.multiselect(
    "Select the product category",
    options=categories,
    default=categories)

if year:
    year_list = year
else:
    year_list = years

if country:
    country_list = country
else:
    country_list = countries

if gender:
    gender_list = gender
else:
    gender_list = genders

if category:
    category_list = category
else:
    category_list = categories

df_selection = df.query("Year == @year_list & SalesTerritoryCountry == @country_list & Gender == @gender_list & EnglishProductCategoryName == @category_list")
df_selection_country = df.query("Year == @year_list & Gender == @gender_list & EnglishProductCategoryName == @category_list")
df_selection_gender = df.query("Year == @year_list & SalesTerritoryCountry == @country_list & EnglishProductCategoryName == @category_list")
df_selection_category = df.query("Year == @year_list & SalesTerritoryCountry == @country_list & Gender == @gender_list")

# ---- MAINPAGE ----
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

# TOP KPI's

total_sales = df_selection["SalesAmount"].count()
total_sales_amount = df_selection["SalesAmount"].sum()
average_sales = df_selection["SalesAmount"].mean()
top_category = df_selection["EnglishProductCategoryName"].mode()

left_column, middle_column1, middle_column2, right_column = st.columns(4)
with left_column:
    text1 = '<div style="border:2px solid White; padding:10px;"><p style="font-family:sans-serif; color:White; font-size: 25px;">Total Sales: 📖 </p>'
    text2 = f'<p style="font-family:sans-serif; color:White; font-size: 20px;">{total_sales}</p></div>'
    st.markdown(text1, unsafe_allow_html=True)
    st.markdown(text2, unsafe_allow_html=True)
with middle_column1:
    text1 = '<div style="border:2px solid White; padding:10px;"><p style="font-family:sans-serif; color:White; font-size: 25px;">Total Sales Amount: 💰 </p>'
    text2 = f'<p style="font-family:sans-serif; color:White; font-size: 20px;">US $ {total_sales_amount:,.2f}</p></div>'
    st.markdown(text1, unsafe_allow_html=True)
    st.markdown(text2, unsafe_allow_html=True)
with middle_column2:
    text1 = '<div style="border:2px solid White; padding:10px;"><p style="font-family:sans-serif; color:White; font-size: 25px;">Average Sales Amount: 💵 </p>'
    text2 = f'<p style="font-family:sans-serif; color:White; font-size: 20px;">US $ {average_sales:,.2f}</p></div>'
    st.markdown(text1, unsafe_allow_html=True)
    st.markdown(text2, unsafe_allow_html=True)
with right_column:
    text1 = '<div style="border:2px solid White; padding:10px;"><p style="font-family:sans-serif; color:White; font-size: 25px;">Top Category: 🏆 </p>'
    text2 = f'<p style="font-family:sans-serif; color:White; font-size: 20px;">{top_category[0]}</p></div>'
    st.markdown(text1, unsafe_allow_html=True)
    st.markdown(text2, unsafe_allow_html=True)

st.divider()

# ---- CHARTS ----

# ---- TOTAL SALES AMOUNT vs TOTAL COST BY COUNTRY ----
chart1 = df_selection_country.groupby("SalesTerritoryCountry").sum()[["SalesAmount", "TotalProductCost"]]
fig_chart1 = px.bar(
    chart1,
    x=chart1.index,
    y=["SalesAmount", "TotalProductCost"],
    title="<b>TOTAL SALES AMOUNT vs TOTAL COST BY COUNTRY</b>",
    template="plotly_white",
    barmode="group",
    color_discrete_sequence=["#FFD184", "#E2AA00"],
    text_auto="$.2s"
)

fig_chart1.update_layout(
    autosize=True,
    uniformtext_minsize=12,
    uniformtext_mode='hide',
    yaxis_title=None,
    xaxis_title=None,
    yaxis={'visible':False, 'showticklabels':False},
    xaxis=dict(tickfont=dict(size=14)),
    legend=dict(orientation='h', yanchor='top', xanchor='center', x=0.5, y=-0.15, title=None, font=dict(size=15)),
    title={'x':0.5, 'xanchor':'center'}
)

fig_chart1.update_traces(textposition="outside", marker_line_color='#00172B', marker_line_width=4, opacity=1)

# ---- TOTAL OF SALES BY MONTH ----

chart2 = df_selection.groupby("Month", as_index=False).sum()[["Month", "OrderQuantity"]]
chart2["Month"]=pd.Categorical(chart2["Month"],["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
chart2.sort_values("Month", inplace=True, ascending=False)
fig_chart2 = px.bar(
    chart2,
    x=["OrderQuantity"],
    y=chart2.Month,
    title="<b>TOTAL OF SALES BY MONTH</b>",
    template="plotly_white",
    orientation="h",
    text_auto=True,
    color_discrete_sequence=["#4472C4"]
)

fig_chart2.update_layout(
    uniformtext_minsize=12,
    uniformtext_mode='hide',
    yaxis_title=None,
    xaxis_title=None,
    xaxis={'visible':False, 'showticklabels':False},
    yaxis=dict(tickfont=dict(size=14)),
    height=900,
    showlegend=False,
    title={'x':0.5, 'xanchor':'center'}
)

fig_chart2.update_traces(textposition="inside", marker_line_color=None,
                         marker_line_width=0, opacity=1)

# ---- SALES BY CATEGORY ----

chart3 = df_selection_category.groupby("EnglishProductCategoryName").sum()[["OrderQuantity"]]
fig_chart3 = px.pie(
    chart3,
    values="OrderQuantity",
    title="<b>SALES BY CATEGORY</b>",
    names=chart3.index,
    color_discrete_sequence=["#4472C4", "#5B9BD5", "#A5A5A5"]
)

fig_chart3.update_layout(
    uniformtext_minsize=14,
    uniformtext_mode='hide',
    height=400,
    title={'x':0.5, 'xanchor':'center'}
)

fig_chart3.update_traces(
    hoverinfo='label+percent',
    marker=dict(line=dict(color="#00172B", width=4)))

# ---- SALES BY GENDER ----

chart4 = df_selection_gender.groupby("Gender").sum()[["OrderQuantity"]]
fig_chart4 = px.pie(
    chart4,
    values="OrderQuantity",
    title="<b>SALES BY GENDER</b>",
    hole=.45,
    names=chart4.index,
    color_discrete_sequence=["#FFD184", "#E2AA00"]
)

fig_chart4.update_layout(
    uniformtext_minsize=14,
    uniformtext_mode='hide',
    height=380,
    title={'x':0.5, 'xanchor':'center'}
)

fig_chart4.update_traces(
    insidetextfont={'color':'black'},
    hoverinfo='label+percent', textinfo='percent+label',
    marker=dict(line=dict(color="#00172B", width=4)),
    showlegend=False
)

# ---- PLACING CHARTS ON MAIN PAGE ----

left_column, right_column = st.columns(2)

with left_column:
    st.plotly_chart(fig_chart1, use_container_width=True)
    left_column1, right_column1 = st.columns(2)
    left_column1.plotly_chart(fig_chart3, use_container_width=True)
    right_column1.plotly_chart(fig_chart4, use_container_width=True)
    right_column.plotly_chart(fig_chart2, use_container_width=True)
