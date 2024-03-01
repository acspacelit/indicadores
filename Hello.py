import streamlit as st

def welcome_page():
    st.title("¡Bienvenido al Dashboard de Análisis de Eficiencia Operativa!")
    st.markdown(
        """
        Esta aplicación te permite:
        
        - Explorar y analizar datos de eficiencia operativa de estaciones en varios países.
        - Visualizar métricas clave, como el tiempo promedio de proyectos, el total de proyectos por estación y país, 
          así como el aporte financiero de FONPLATA.
        - Utilizar gráficos interactivos que te ayudarán a entender mejor la distribución de KPI promedio por país y estación, 
          el porcentaje de aporte FONPLATA por país y el recuento de IDEtapas por sector.
        
        ¡Explora los diferentes filtros y gráficos para obtener información valiosa sobre la eficiencia operativa de las 
        estaciones de FONPLATA!
        """
    )

if __name__ == "__main__":
    welcome_page()
