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
#categorias = ["Autopista", "Carretera Pavimento Dos Vias o Mas", "Carretera Pavimento Una Via",
#              "Carretera Sin Pavimento Dos Vias", "Camino de Tierra"]
categorias = redvial.categoria.unique().tolist()
categorias.sort()

for cat in categorias:
    temp_join = rv_cant_cat_agrupado.loc[rv_cant_cat_agrupado["categoria"] == cat][
        ["cod_canton", "longitud_intersect"]]
    tabla_cant = tabla_cant.join(temp_join.set_index('cod_canton'), on='cod_canton', rsuffix='_b')
    tabla_cant.rename(columns={'longitud_intersect': cat}, inplace=True)
    tabla_cant[cat] = tabla_cant[cat].fillna(0)

tabla_cant = tabla_cant.sort_values("cod_canton", ascending=[True])

# Configuracion del Sidebar

filtro_categoria = st.sidebar.selectbox('Seleccione la Categoría de Vía', categorias)

# 1. Tabla de Cantones

st.markdown('Tabla de Densidad Vial por Categoria de Via y Cantón.')
print_tabla_cant = tabla_cant[['cod_canton','Canton','Area',filtro_categoria]]
print_tabla_cant = pd.DataFrame(print_tabla_cant)
print_tabla_cant["Densidad"] = print_tabla_cant[filtro_categoria] / print_tabla_cant['Area']
print_tabla_cant = print_tabla_cant.rename(columns={filtro_categoria: filtro_categoria.title()})
print_tabla_cant
