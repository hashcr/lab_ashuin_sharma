# !/usr/bin/env python
# coding: utf-8
# Autor: Ashuin Sharma (A35029)
# Proyecto de Laboratorio curso Ciencia de Datos Geoespaciales con Python .

import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import plotly.express as px
from streamlit_folium import folium_static

# Configugraciones y Leyendas de la Aplicacion
st.set_page_config(layout='wide')

st.title('Dashboard - Visualización de Datos Sobre Densidad Vial')
st.markdown('Esta aplicación presenta visualizaciones tabulares, gráficas y geoespaciales de datos sobre la red vial nacional en los distintos cantones de Costa Rica..')
st.markdown('El usuario debe seleccionar en la barra lateral una de las 5 distintas categorias de Via y la aplicación le mostrará los datos correspondientes.')
st.markdown('1- Tabla de datos por cantones 2- Gráfico de Barras  3- Gráfico de Pastel  4- Mapa de Coropletas.')
st.markdown('Código Fuente: https://github.com/hashcr/lab_ashuin_sharma/Dashboard_Laboratorio_AshuinSharma.py')

# 0. Preparación de datos y cálculos.
cantones = gpd.read_file("cantones.geojson")
redvial = gpd.read_file("redvial.geojson")
redvial = redvial[["categoria", "geometry"]]
cantones = cantones[["cod_canton", "canton", "geometry", "area"]]
cantones["area"] = cantones["geometry"].area / 1000000
redvial_cantones = redvial.overlay(cantones, how="intersection")
redvial_cantones["longitud_intersect"] = redvial_cantones['geometry'].length / 1000
rv_cant_cat_agrupado = redvial_cantones.groupby(["cod_canton", "canton", "area", "categoria"])[
    "longitud_intersect"].sum()
rv_cant_cat_agrupado = rv_cant_cat_agrupado.reset_index()
rv_cant_agrupado = rv_cant_cat_agrupado.groupby(["cod_canton"])["longitud_intersect"].sum()
rv_cant_agrupado = rv_cant_agrupado.reset_index()
tabla_cant = cantones.join(rv_cant_agrupado.set_index('cod_canton'), on='cod_canton', rsuffix='_b')
tabla_cant.rename(columns={'longitud_intersect': 'Longitud Total', 'area': 'Area', 'canton': 'Canton'}, inplace=True)
tabla_cant["Densidad Total"] = tabla_cant["Longitud Total"] / tabla_cant["Area"];
categorias = redvial.categoria.unique().tolist()
categorias.sort()

for cat in categorias:
    temp_join = rv_cant_cat_agrupado.loc[rv_cant_cat_agrupado["categoria"] == cat][
        ["cod_canton", "longitud_intersect"]]
    tabla_cant = tabla_cant.join(temp_join.set_index('cod_canton'), on='cod_canton', rsuffix='_b')
    tabla_cant.rename(columns={'longitud_intersect': cat}, inplace=True)
    tabla_cant[cat] = tabla_cant[cat].fillna(0)

tabla_cant = tabla_cant.sort_values("cod_canton", ascending=[True]).reset_index()

# 1. Configuracion del Sidebar y Columnas

filtro_categoria = st.sidebar.selectbox('Seleccione la Categoría de Vía', categorias)
# Definición de columnas
col1, col2 = st.columns(2)

# 2. Tabla de Cantones
with col1:
    st.header('1. Tabla de Densidad Vial por Categoria de Via y Cantón.')
    print_tabla_cant = tabla_cant[['cod_canton','Canton','Area',filtro_categoria]]
    print_tabla_cant = pd.DataFrame(print_tabla_cant)
    print_tabla_cant["Densidad"] = print_tabla_cant[filtro_categoria] / print_tabla_cant['Area']
    st.dataframe(print_tabla_cant[['Canton',filtro_categoria,'Densidad']]
                 .rename(columns={'Canton': 'Cantón', filtro_categoria: filtro_categoria.title()}), height=600)

# 3. Gráfico de Barras
# Dataframe filtrado con los top 15 cantones como mayor red vial, para usar en graficación
with col2:
    st.header('2. Gráfico de Barras Apiladas por Tipo de Via.')
    print_grafico_barras = print_tabla_cant.sort_values(filtro_categoria, ascending=[False]).head(15)
    fig = px.bar(print_grafico_barras,
                 x='Canton',
                 y=filtro_categoria,
                 title="Top 15 cantones con mayor longitud de red vial de tipo : {}.".format(filtro_categoria.title()),
                 height=600,
                 labels={
                     filtro_categoria: "Longitud (Km)"
                 })
    st.plotly_chart(fig)

# 4. Gráfico de Pastel
# Pie Chart con la propocion de los 15 principales cantones con Densidad Vial por Determinado Tipo de Via.

st.header('3. Gráfico de Pastel Longitud Total por Tipo de Via y Cantón.')
print_grafico_pie = print_tabla_cant.sort_values(filtro_categoria, ascending=[False])
print_grafico_pie.loc[print_grafico_pie[filtro_categoria] < print_grafico_pie.iloc[14][filtro_categoria],
                      'Canton']= 'Otros'
# Creación del Pie Chart
fig = px.pie(print_grafico_pie, values=filtro_categoria, names='Canton', height=600,
             title='Gráfico de Pastel. Distribución Total de Red Vial por Cantones y Tipo Via: {}'
                .format(filtro_categoria.title()))
st.plotly_chart(fig)

# 5. Mapa de coropletas Densidad Vial de Costa Rica.
# Creación del mapa base

st.header('4. Mapa de coropletas Densidad Vial de Costa Rica por Tipo de Via y Cantón.')
m = folium.Map(location=[9.8, -84],
               tiles='CartoDB positron',
               control_scale=True,
               zoom_start=7)

# Creación del mapa de coropletas
folium.Choropleth(
    name="Densidad Vial",
    geo_data=cantones,
    data=print_tabla_cant,
    columns=['cod_canton', 'Densidad'],
    bins=7,
    key_on='feature.properties.cod_canton',
    fill_color='Reds',
    fill_opacity=0.8,
    line_opacity=1,
    legend_name='Densidad vial por Cantón y Via Categoria tipo {}'.format(filtro_categoria.title()),
    smooth_factor=0).add_to(m)

# Añadir capa de Red Vial
folium.GeoJson(data=redvial[redvial['categoria'] == filtro_categoria], name='Red vial').add_to(m)

# Control de capas
folium.LayerControl().add_to(m)
folium_static(m)