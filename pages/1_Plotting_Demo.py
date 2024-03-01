import streamlit as st
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración inicial de la página
st.set_page_config(page_title="Análisis de Eficiencia Operativa", page_icon="📊")

# URLs de las hojas de Google Sheets
estaciones = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ3uglhp1iEb6nz_Rjh6SnKyt0GqaAxOwGIqsQEdgcwJfrSP2wOZqFfrIjKL3KfsLzi4sSq2HJ3nkAt/pub?gid=0&single=true&output=csv"

# Función para cargar los datos desde la URL
def load_data_from_url(url):
    try:
        return pd.read_csv(url, header=0)
    except Exception as e:
        st.error("Error al cargar los datos: " + str(e))
        return None

def clean_numeric_column(column):
    return pd.to_numeric(column.str.replace(',', '.'), errors='coerce')

def main():
    # Título de la aplicación
    st.title('Dashboard de Streamlit')

    # Carga los datos
    data = load_data_from_url(estaciones)

    # Limpiar columnas numéricas
    data['KPI'] = clean_numeric_column(data['KPI'])
    data['AporteFONPLATAVigente'] = clean_numeric_column(data['AporteFONPLATAVigente'])

    # Widgets para interactividad
    years = data['AÑO'].dropna().astype(int)
    min_year, max_year = int(years.min()), int(years.max())
    selected_years = st.slider('Selecciona el rango de años:', min_year, max_year, (min_year, max_year))

    # Listado de estaciones sin la opción 'Todas'
    all_stations = list(data['Estaciones'].dropna().unique())
    selected_station = st.selectbox('Selecciona una Estación', all_stations)

    # Filtro por país con la opción "Todos"
    all_countries = ['Todos'] + list(data['Pais'].dropna().unique())
    selected_countries = st.multiselect('Selecciona Países', all_countries, default='Todos')

    # Aplicar filtros al DataFrame basado en la selección de estaciones y países
    filtered_df = data[
        (data['AÑO'] >= selected_years[0]) &
        (data['AÑO'] <= selected_years[1])
    ]

    # Filtro por estación seleccionada
    filtered_df = filtered_df[filtered_df['Estaciones'] == selected_station]

    # Filtro por países seleccionados
    if 'Todos' not in selected_countries:
        filtered_df = filtered_df[filtered_df['Pais'].isin(selected_countries)]

    st.header("         Análisis de la Eficiencia Operativa")

    # Cálculos previos de tus métricas
    average_kpi = filtered_df['KPI'].mean()
    unique_operation_count = filtered_df['IDEtapa'].nunique()
    total_stations = (filtered_df['AporteFONPLATAVigente'].sum() / 1_000_000).round(2)

    Infraestructura = filtered_df[filtered_df['SEC'] == 'INF']
    inf_operation = len(Infraestructura)

    Social = filtered_df[filtered_df['SEC'] == 'SOC']
    soc_operation = len(Social)

    Productivo = filtered_df[filtered_df['SEC'] == 'PRO']
    pro_operation = len(Productivo)

    # Primera fila de tarjetas
    row1_cols = st.columns(3)  # Esto crea tres columnas para la primera fila

    with row1_cols[0]:
        st.metric(
            label="Tiempo Promedio",
            value=f"{average_kpi:.2f} Meses",
            delta="Promedio de KPI"
        )

    with row1_cols[1]:
        st.metric(
            label="Proyectos Totales",
            value=str(unique_operation_count),
            delta="Total de proyectos únicos"
        )

    with row1_cols[2]:
        st.metric(
            label="Aporte Fonplata",
            value=f"${total_stations}M",
            delta="En millones de dólares"
        )

    # Segunda fila de tarjetas
    row2_cols = st.columns(3)  # Esto crea tres columnas para la segunda fila

    with row2_cols[0]:
        st.metric(
            label="Infraestructura",
            value=str(inf_operation),
            delta="Proyectos de Infraestructura"
        )

    with row2_cols[1]:
        st.metric(
            label="Socio-Económicos",
            value=str(soc_operation),
            delta="Proyectos Socio-Económicos"
        )

    with row2_cols[2]:
        st.metric(
            label="Productivos",
            value=str(pro_operation),
            delta="Proyectos Productivos"
        )

    # Pivotear el DataFrame para obtener el KPI promedio por país y año
    kpi_pivot_df = filtered_df.pivot_table(values='KPI', index='Pais', columns='AÑO', aggfunc='mean')

    # Redondear todos los valores numéricos a dos decimales
    kpi_pivot_df = kpi_pivot_df.round(2)

    # Opción para reemplazar los valores None/NaN con un string vacío
    kpi_pivot_df = kpi_pivot_df.fillna('')

    # Convertir las etiquetas de las columnas a enteros (los años)
    kpi_pivot_df.columns = kpi_pivot_df.columns.astype(int)

    # Resetear el índice para llevar 'ESTACIONES' a una columna
    kpi_pivot_df.reset_index(inplace=True)

    # Preparar los datos para el gráfico
    kpi_avg_by_country_station = filtered_df.groupby(['Pais', 'Estaciones'])['KPI'].mean().reset_index()

    # Definir el esquema de color personalizado
    color_scheme = {
        "Aprobacion": "lightgreen",
        "Vigencia": "skyblue",
        "PrimerDesembolso": "salmon",
        "Elegibilidad": "gold"
    }

    # Gráfico de barras
    bars = alt.Chart(kpi_avg_by_country_station).mark_bar().encode(
        x=alt.X('Pais:N', title='País'),
        y=alt.Y('mean(KPI):Q', title='KPI Promedio'),
        color=alt.Color('Estaciones:N', scale=alt.Scale(domain=list(color_scheme.keys()), range=list(color_scheme.values())), legend=alt.Legend(title="Estaciones")),
        tooltip=['Pais', 'Estaciones', 'mean(KPI)']
    ).properties(
        title='KPI Promedio por País y Estación',
        width=600,
        height=400
    )

    # Gráfico de texto para mostrar los totales
    text = bars.mark_text(
        align='center',
        baseline='bottom',
        dy=-5  # Ajusta la posición del texto respecto a la parte superior de la barra
    ).encode(
        text=alt.Text('mean(KPI):Q', format='.2f')  # Formatea el número a 2 decimales
    )

    # Combinar los gráficos de barras y texto
    combined_chart = alt.layer(bars, text)

    st.altair_chart(combined_chart, use_container_width=True)

    # Calcular la suma de AporteFONPLATAVigente por país en el DataFrame filtrado
    aporte_por_pais = filtered_df.groupby('Pais')['AporteFONPLATAVigente'].sum().reset_index()

    # Calcular el total de AporteFONPLATAVigente para calcular porcentajes
    total_aporte = aporte_por_pais['AporteFONPLATAVigente'].sum()

    # Agregar una columna de porcentaje al DataFrame
    aporte_por_pais['Porcentaje'] = (aporte_por_pais['AporteFONPLATAVigente'] / total_aporte) * 100

    # Definir la paleta de colores para los países
    country_colors = {
        "Argentina": "#36A9E1",
        "Bolivia": "#F39200",
        "Brasil": "#009640",
        "Paraguay": "#E30613",
        "Uruguay": "#27348B"
    }

    # Calcula los valores totales y los porcentajes
    aporte_total_por_pais = filtered_df.groupby('Pais')['AporteFONPLATAVigente'].sum().reset_index()
    aporte_total_por_pais['Porcentaje'] = (aporte_total_por_pais['AporteFONPLATAVigente'] / aporte_total_por_pais['AporteFONPLATAVigente'].sum()) * 100

    # Define los colores de cada país según la paleta personalizada
    colors = [country_colors[pais] for pais in aporte_total_por_pais['Pais']]

    # Crea el gráfico de anillo
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        aporte_total_por_pais['Porcentaje'],
        labels=aporte_total_por_pais['Pais'],
        autopct='%1.1f%%',  # Esto añade la etiqueta de porcentaje automáticamente
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.6, edgecolor='w')  # Esto crea el anillo con un borde blanco
    )

    # Personaliza las etiquetas de porcentaje
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('white')

    # Título del gráfico
    plt.title('Porcentaje de Aporte FONPLATA Vigente por País')

    # Mostrar el gráfico
    st.pyplot(fig)

    # Calcular la suma de AporteFONPLATAVigente por país y convertirlo a millones
    aporte_total_por_pais = filtered_df.groupby('Pais')['AporteFONPLATAVigente'].sum().reset_index()
    aporte_total_por_pais['AporteFONPLATAVigente_Millones'] = (aporte_total_por_pais['AporteFONPLATAVigente'] / 1_000_000).round(2)

    # Gráfico de barras para mostrar el total de AporteFONPLATAVigente en millones por país
    bar_chart = alt.Chart(aporte_total_por_pais).mark_bar().encode(
        x=alt.X('Pais:N', title='País'),
        y=alt.Y('AporteFONPLATAVigente_Millones:Q', title='Total de Aporte FONPLATA Vigente (en millones)'),
        color=alt.Color('Pais:N', scale=alt.Scale(domain=list(country_colors.keys()), range=list(country_colors.values()))),
        tooltip=[alt.Tooltip('Pais:N', title='País'), alt.Tooltip('AporteFONPLATAVigente_Millones:Q', title='Aporte FONPLATA Vigente (millones)', format='.2f')]
    )

    # Etiquetas de texto para cada barra
    text = bar_chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5  # Nudge text to sit atop bars
    ).encode(
        text=alt.Text('AporteFONPLATAVigente_Millones:Q', format='.2f')
    )

    # Combinar los gráficos de barras y texto
    combined_chart = alt.layer(bar_chart, text).properties(
        title="Total de Aporte FONPLATA Vigente por País (en millones)"
    )

    st.altair_chart(combined_chart, use_container_width=True)

    # Convertir la columna 'Sector' a un tipo de datos nominal
    filtered_df['Sector'] = filtered_df['SEC'].astype('category')

    # Contar el recuento distintivo de IDEtapa para cada sector
    count_by_sector = filtered_df.groupby('Sector')['IDEtapa'].nunique().reset_index()

    # Definir la paleta de colores
    sector_colors = {
        'INF': '#F2D030',
        'PRO': '#F04343',
        'SOC': '#20EDB6'
    }

    # Crear el gráfico de barras con Altair y la paleta de colores personalizada
    bar_chart = alt.Chart(count_by_sector).mark_bar().encode(
        x=alt.X('Sector:N', title='Sector'),
        y=alt.Y('IDEtapa:Q', title='Recuento Distintivo de IDEtapa'),
        tooltip=['Sector', 'IDEtapa'],
        color=alt.Color('Sector:N', legend=None, scale=alt.Scale(domain=list(sector_colors.keys()), range=list(sector_colors.values())))
    ).properties(
        title='Recuento Distintivo de IDEtapa por Sector'
    )

    # Añadir etiquetas de valores encima de las barras
    text = bar_chart.mark_text(
        align='center',
        baseline='middle',
        dy=-5  # ajuste de posición vertical
    ).encode(
        text='IDEtapa:Q'
    )

    # Combinar gráfico de barras y etiquetas de texto
    combined_chart = (bar_chart + text)

    # Mostrar el gráfico
    st.altair_chart(combined_chart, use_container_width=True)

    # Filtrar el DataFrame para obtener solo las filas con 'Productividad' igual a 'Alta Demora'
    proyectos_alta_demora = filtered_df[filtered_df['Productividad'] == 'Alta Demora']

    # Mostrar un subheader
    st.subheader("Proyectos con Alta Demora")

    # Mostrar una tabla con los datos filtrados
    st.dataframe(proyectos_alta_demora[['APODO', 'Pais', 'Estaciones', 'KPI']])
    # Filtrar el DataFrame para obtener solo las filas con 'Productividad' igual a 'Alta Demora'
    proyectos_alta_demora = filtered_df[filtered_df['Productividad'] == 'Con Demora']

    # Mostrar un subheader
    st.subheader("Proyectos con Demora")

    # Mostrar una tabla con los datos filtrados
    st.dataframe(proyectos_alta_demora[['APODO', 'Pais', 'Estaciones', 'KPI']])

# Llamar a la función principal para ejecutar la aplicación
if __name__ == "__main__":
    main()


