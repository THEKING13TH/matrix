import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import io
from datetime import datetime
import warnings
import openpyxl  # Asegúrate de tenerlo instalado

warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Dinámico Excel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .stSelectbox > div > div > select {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

class ExcelDashboard:
    def __init__(self):
        self.df = None
        self.numeric_columns = []
        self.categorical_columns = []
        self.datetime_columns = []
        
    def load_data(self, uploaded_file):
        """Carga y procesa el archivo Excel"""
        try:
            # Leer el archivo Excel
            if uploaded_file.name.endswith('.xlsx'):
                self.df = pd.read_excel(uploaded_file, engine='openpyxl')
            elif uploaded_file.name.endswith('.xls'):
                self.df = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                st.error("Formato de archivo no soportado. Use .xlsx o .xls")
                return False
            
            # Procesar tipos de datos
            self.process_data_types()
            return True
            
        except Exception as e:
            st.error(f"Error al cargar el archivo: {str(e)}")
            return False
    
    def process_data_types(self):
        """Identifica y clasifica los tipos de datos"""
        self.numeric_columns = list(self.df.select_dtypes(include=[np.number]).columns)
        self.categorical_columns = list(self.df.select_dtypes(include=['object']).columns)
        
        # Intentar convertir columnas de fecha
        for col in self.categorical_columns.copy():
            try:
                self.df[col] = pd.to_datetime(self.df[col], errors='raise')
                self.datetime_columns.append(col)
                self.categorical_columns.remove(col)
            except:
                continue
    
    def get_basic_stats(self):
        """Genera estadísticas básicas del dataset"""
        stats = {
            'filas': len(self.df),
            'columnas': len(self.df.columns),
            'valores_nulos': self.df.isnull().sum().sum(),
            'memoria_mb': round(self.df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
        return stats
    
    def create_correlation_heatmap(self):
        """Crea un mapa de calor de correlaciones"""
        if len(self.numeric_columns) < 2:
            return None
        
        correlation_matrix = self.df[self.numeric_columns].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmin=-1, zmax=1,
            text=correlation_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Matriz de Correlación",
            xaxis_title="Variables",
            yaxis_title="Variables",
            height=600
        )
        
        return fig
    
    def create_distribution_plots(self):
        """Crea gráficos de distribución para variables numéricas"""
        if not self.numeric_columns:
            return None
        
        n_cols = min(3, len(self.numeric_columns))
        n_rows = (len(self.numeric_columns) + n_cols - 1) // n_cols
        
        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=self.numeric_columns,
            vertical_spacing=0.1
        )
        
        for i, col in enumerate(self.numeric_columns):
            row = i // n_cols + 1
            col_pos = i % n_cols + 1
            
            fig.add_trace(
                go.Histogram(x=self.df[col], name=col, showlegend=False),
                row=row, col=col_pos
            )
        
        fig.update_layout(
            title="Distribución de Variables Numéricas",
            height=300 * n_rows,
            showlegend=False
        )
        
        return fig
    
    def create_categorical_plots(self):
        """Crea gráficos para variables categóricas"""
        if not self.categorical_columns:
            return None
        
        plots = []
        for col in self.categorical_columns[:4]:  # Límite de 4 gráficos
            value_counts = self.df[col].value_counts().head(10)
            
            fig = px.bar(
                x=value_counts.values,
                y=value_counts.index,
                orientation='h',
                title=f"Distribución de {col}",
                labels={'x': 'Frecuencia', 'y': col}
            )
            fig.update_layout(height=400)
            plots.append(fig)
        
        return plots
    
    def create_time_series_plots(self):
        """Crea gráficos de series de tiempo si hay columnas de fecha"""
        if not self.datetime_columns or not self.numeric_columns:
            return None
        
        plots = []
        for date_col in self.datetime_columns:
            for num_col in self.numeric_columns[:3]:  # Límite de 3 variables numéricas
                df_sorted = self.df.sort_values(date_col)
                
                fig = px.line(
                    df_sorted,
                    x=date_col,
                    y=num_col,
                    title=f"Evolución temporal: {num_col}"
                )
                fig.update_layout(height=400)
                plots.append(fig)
        
        return plots
    
    def create_scatter_matrix(self):
        """Crea una matriz de gráficos de dispersión"""
        if len(self.numeric_columns) < 2:
            return None
        
        # Limitar a las primeras 5 variables numéricas para evitar sobrecarga
        cols_to_use = self.numeric_columns[:5]
        
        fig = px.scatter_matrix(
            self.df,
            dimensions=cols_to_use,
            title="Matriz de Dispersión - Variables Numéricas"
        )
        fig.update_layout(height=800)
        
        return fig

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard Dinámico para Archivos Excel</h1>
        <p>Carga tu archivo Excel y genera automáticamente estadísticas y visualizaciones interactivas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar el dashboard
    dashboard = ExcelDashboard()
    
    # Sidebar para carga de archivos
    st.sidebar.header("📁 Carga de Archivo")
    uploaded_file = st.sidebar.file_uploader(
        "Selecciona un archivo Excel",
        type=['xlsx', 'xls'],
        help="Soporta formatos .xlsx y .xls"
    )
    
    if uploaded_file is not None:
        # Cargar datos
        with st.spinner("Cargando archivo..."):
            if dashboard.load_data(uploaded_file):
                st.success(f"✅ Archivo '{uploaded_file.name}' cargado exitosamente!")
                
                # Estadísticas básicas
                stats = dashboard.get_basic_stats()
                
                # Métricas principales
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="📊 Total de Filas",
                        value=f"{stats['filas']:,}"
                    )
                
                with col2:
                    st.metric(
                        label="📋 Columnas",
                        value=stats['columnas']
                    )
                
                with col3:
                    st.metric(
                        label="❌ Valores Nulos",
                        value=f"{stats['valores_nulos']:,}"
                    )
                
                with col4:
                    st.metric(
                        label="💾 Tamaño (MB)",
                        value=f"{stats['memoria_mb']}"
                    )
                
                # Tabs para diferentes vistas
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "📋 Vista de Datos", 
                    "📈 Estadísticas", 
                    "🔍 Correlaciones", 
                    "📊 Distribuciones",
                    "🎯 Análisis Avanzado",
                    "🏢 Equipos por Municipio"  # Nueva pestaña
                ])
                
                with tab1:
                    st.header("Vista Previa de los Datos")
                    
                    # Filtros interactivos
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        show_columns = st.multiselect(
                            "Selecciona columnas a mostrar:",
                            dashboard.df.columns.tolist(),
                            default=dashboard.df.columns.tolist()[:10]
                        )
                    
                    with col2:
                        num_rows = st.slider(
                            "Número de filas a mostrar:",
                            min_value=10,
                            max_value=min(1000, len(dashboard.df)),
                            value=100
                        )
                    
                    # Mostrar datos filtrados
                    if show_columns:
                        df_preview = dashboard.df[show_columns].head(num_rows).reset_index(drop=True)
                        df_preview.index = df_preview.index + 1  # Índice desde 1
                        st.dataframe(df_preview, use_container_width=True, height=400)
                    
                    # Información de columnas
                    st.subheader("Información de Columnas")
                    col_info = pd.DataFrame({
                        'Columna': dashboard.df.columns,
                        'Tipo': dashboard.df.dtypes,
                        'Valores Nulos': dashboard.df.isnull().sum(),
                        '% Nulos': (dashboard.df.isnull().sum() / len(dashboard.df) * 100).round(2),
                        'Valores Únicos': dashboard.df.nunique()
                    })
                    st.dataframe(col_info, use_container_width=True)
                
                with tab2:
                    st.header("Estadísticas Descriptivas")
                    
                    # Selector de columnas numéricas
                    selected_numeric = st.multiselect(
                        "Selecciona variables numéricas para estadísticas:",
                        dashboard.numeric_columns,
                        default=dashboard.numeric_columns[:5]
                    )
                    # Selector de columnas categóricas
                    selected_categorical = st.multiselect(
                        "Selecciona variables categóricas para estadísticas:",
                        dashboard.categorical_columns,
                        default=dashboard.categorical_columns[:3]
                    )
                    
                    if selected_numeric:
                        st.subheader("📊 Variables Numéricas")
                        numeric_stats = dashboard.df[selected_numeric].describe()
                        st.dataframe(numeric_stats, use_container_width=True)
                        
                        fig = go.Figure()
                        for col in selected_numeric:
                            fig.add_trace(go.Box(
                                y=dashboard.df[col],
                                name=col,
                                boxpoints='outliers'
                            ))
                        fig.update_layout(
                            title="Distribución y Outliers - Variables Numéricas",
                            yaxis_title="Valores",
                            height=500
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if selected_categorical:
                        st.subheader("📝 Estadísticas Categóricas Compuestas")
                        chart_type = st.selectbox("Tipo de gráfica:", ["Barra", "Pie", "Línea", "Histograma"], index=0)
                        # Lista de colores con nombre y código
                        color_options = [
                            ("Azul", "#636EFA"),
                            ("Rojo", "#EF553B"),
                            ("Verde", "#00CC96"),
                            ("Morado", "#AB63FA"),
                            ("Naranja", "#FFA15A"),
                            ("Cian", "#19D3F3"),
                            ("Rosa", "#FF6692"),
                            ("Lima", "#B6E880"),
                        ]

                        # Ejemplo para una columna categórica
                        if len(selected_categorical) == 1:
                            col = selected_categorical[0]
                            value_counts = dashboard.df[col].value_counts()
                            # Selector con color y nombre
                            selected_color = st.selectbox(
                                f"Color para {col}:",
                                color_options,
                                format_func=lambda x: f"🟦 {x[0]}" if x[0] == "Azul" else
                                                     f"🟥 {x[0]}" if x[0] == "Rojo" else
                                                     f"🟩 {x[0]}" if x[0] == "Verde" else
                                                     f"🟪 {x[0]}" if x[0] == "Morado" else
                                                     f"🟧 {x[0]}" if x[0] == "Naranja" else
                                                     f"🟦 {x[0]}" if x[0] == "Cian" else
                                                     f"🟪 {x[0]}" if x[0] == "Rosa" else
                                                     f"🟩 {x[0]}" if x[0] == "Lima" else x[0],
                                index=0
                            )
                            color_code = selected_color[1]

                            fig = None
                            if chart_type == "Barra":
                                fig = px.bar(
                                    value_counts,
                                    x=value_counts.index,
                                    y=value_counts.values,
                                    title=f"Distribución de {col}",
                                    color_discrete_sequence=[color_code]
                                )
                            elif chart_type == "Pie":
                                fig = px.pie(
                                    values=value_counts.values,
                                    names=value_counts.index,
                                    title=f"Distribución de {col}",
                                    color_discrete_sequence=[color_code]
                                )
                            elif chart_type == "Línea":
                                fig = px.line(
                                    x=value_counts.index,
                                    y=value_counts.values,
                                    title=f"Distribución de {col}",
                                    color_discrete_sequence=[color_code]
                                )
                            elif chart_type == "Histograma":
                                fig = px.histogram(
                                    x=dashboard.df[col],
                                    title=f"Distribución de {col}",
                                    color_discrete_sequence=[color_code]
                                )
                            if fig is not None:
                                st.plotly_chart(fig, use_container_width=True)
                            st.markdown(f"**Total de registros:** {len(dashboard.df)}")
                        else:
                            group = dashboard.df.groupby(selected_categorical).size().reset_index(name='Conteo')
                            group.index = group.index + 1  # Índice desde 1
                            st.dataframe(group, use_container_width=True)
                            if len(selected_categorical) == 2:
                                color_map = {}
                                for cat in dashboard.df[selected_categorical[1]].unique():
                                    color_tuple = st.selectbox(
                                        f"Color para {cat} en {selected_categorical[1]}:",
                                        color_options,
                                        format_func=lambda x: f"🟦 {x[0]}" if x[0] == "Azul" else
                                                             f"🟥 {x[0]}" if x[0] == "Rojo" else
                                                             f"🟩 {x[0]}" if x[0] == "Verde" else
                                                             f"🟪 {x[0]}" if x[0] == "Morado" else
                                                             f"🟧 {x[0]}" if x[0] == "Naranja" else
                                                             f"🟦 {x[0]}" if x[0] == "Cian" else
                                                             f"🟪 {x[0]}" if x[0] == "Rosa" else
                                                             f"🟩 {x[0]}" if x[0] == "Lima" else x[0],
                                        index=0
                                    )
                                    color_map[cat] = color_tuple[1]
                                
                                if chart_type == "Barra":
                                    fig = px.bar(
                                        group,
                                        x=selected_categorical[0],
                                        y='Conteo',
                                        color=selected_categorical[1],
                                        title=f"Distribución compuesta: {' y '.join(selected_categorical)}",
                                        color_discrete_map=color_map
                                    )
                                elif chart_type == "Línea":
                                    fig = px.line(
                                        group,
                                        x=selected_categorical[0],
                                        y='Conteo',
                                        color=selected_categorical[1],
                                        title=f"Distribución compuesta: {' y '.join(selected_categorical)}",
                                        color_discrete_map=color_map
                                    )
                                elif chart_type == "Histograma":
                                    fig = px.histogram(
                                        group,
                                        x=selected_categorical[0],
                                        y='Conteo',
                                        color=selected_categorical[1],
                                        title=f"Distribución compuesta: {' y '.join(selected_categorical)}",
                                        color_discrete_map=color_map
                                    )
                                elif chart_type == "Pie":
                                    fig = px.pie(
                                        group,
                                        names=selected_categorical[0],
                                        values='Conteo',
                                        title=f"Distribución compuesta: {' y '.join(selected_categorical)}",
                                        color_discrete_map=color_map
                                    )
                                st.plotly_chart(fig, use_container_width=True)
                                # Botón para descargar datos agrupados en Excel
                                output = io.BytesIO()
                                group.to_excel(output, index=False)
                                st.download_button(
                                    label="Descargar datos agrupados en Excel",
                                    data=output.getvalue(),
                                    file_name="datos_agrupados.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            else:
                                st.info("Para gráficos apilados, selecciona solo 2 columnas categóricas. La tabla muestra todas las combinaciones.")

                with tab3:
                    st.header("Análisis de Correlaciones")
                    selected_corr = st.multiselect(
                        "Selecciona columnas para correlación (numéricas y/o categóricas):",
                        dashboard.df.columns.tolist(),
                        default=dashboard.numeric_columns[:2] + dashboard.categorical_columns[:1]
                    )
                    if len(selected_corr) >= 2:
                        # Si hay categóricas, convertirlas a códigos numéricos para correlación
                        df_corr = dashboard.df[selected_corr].copy()
                        for col in selected_corr:
                            if df_corr[col].dtype == 'object':
                                df_corr[col] = df_corr[col].astype('category').cat.codes
                        correlation_matrix = df_corr.corr()
                        fig = go.Figure(data=go.Heatmap(
                            z=correlation_matrix.values,
                            x=correlation_matrix.columns,
                            y=correlation_matrix.columns,
                            colorscale='RdBu',
                            zmin=-1, zmax=1,
                            text=correlation_matrix.round(2).values,
                            texttemplate="%{text}",
                            textfont={"size": 10},
                            hoverongaps=False
                        ))
                        fig.update_layout(
                            title="Matriz de Correlación",
                            xaxis_title="Variables",
                            yaxis_title="Variables",
                            height=600
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.subheader("Matriz de Correlación (Valores)")
                        st.dataframe(correlation_matrix.round(3), use_container_width=True)
                    else:
                        st.warning("⚠️ Selecciona al menos 2 columnas para calcular correlaciones.")

                with tab4:
                    st.header("Distribuciones de Variables")
                    selected_dist = st.multiselect(
                        "Selecciona columnas para distribución (numéricas y/o categóricas):",
                        dashboard.df.columns.tolist(),
                        default=dashboard.numeric_columns[:2] + dashboard.categorical_columns[:1]
                    )
                    if selected_dist:
                        if all(dashboard.df[col].dtype != 'object' for col in selected_dist):
                            # Todas numéricas: histogramas
                            fig = make_subplots(
                                rows=1, cols=len(selected_dist),
                                subplot_titles=selected_dist,
                                vertical_spacing=0.1
                            )
                            for i, col in enumerate(selected_dist):
                                fig.add_trace(
                                    go.Histogram(x=dashboard.df[col], name=col, showlegend=False),
                                    row=1, col=i+1
                                )
                            fig.update_layout(
                                title="Distribución de Variables Numéricas",
                                height=400,
                                showlegend=False
                            )
                            st.subheader("📈 Distribuciones Numéricas")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            # Alguna categórica: tabla compuesta y gráfico apilado si son 2
                            group = dashboard.df.groupby(selected_dist).size().reset_index(name='Conteo')
                            st.dataframe(group, use_container_width=True)
                            if len(selected_dist) == 2:
                                fig = px.bar(
                                    group,
                                    x=selected_dist[0],
                                    y='Conteo',
                                    color=selected_dist[1],
                                    title=f"Distribución compuesta: {' y '.join(selected_dist)}"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Para gráficos apilados, selecciona solo 2 columnas. La tabla muestra todas las combinaciones.")

                with tab5:
                    st.header("Análisis Avanzado")
                    selected_advanced = st.multiselect(
                        "Selecciona columnas para análisis avanzado (numéricas y/o categóricas):",
                        dashboard.df.columns.tolist(),
                        default=dashboard.numeric_columns[:2] + dashboard.categorical_columns[:1]
                    )
                    if len(selected_advanced) >= 2:
                        group = dashboard.df.groupby(selected_advanced).size().reset_index(name='Conteo')
                        st.dataframe(group, use_container_width=True)
                        if len(selected_advanced) == 2:
                            fig = px.bar(
                                group,
                                x=selected_advanced[0],
                                y='Conteo',
                                color=selected_advanced[1],
                                title=f"Análisis avanzado: {' y '.join(selected_advanced)}"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Para gráficos apilados, selecciona solo 2 columnas. La tabla muestra todas las combinaciones.")
                    else:
                        st.info("Selecciona al menos 2 columnas para ver el análisis compuesto.")

                with tab6:
                    st.header("Equipos y Estadísticas por Municipio")
                    municipio_col = st.selectbox(
                        "Selecciona la columna de municipios:",
                        dashboard.categorical_columns
                    )
                    equipo_col = st.selectbox(
                        "Selecciona la columna de equipos:",
                        dashboard.categorical_columns
                    )
                    # Agrupar por municipio y equipo
                    group = dashboard.df.groupby([municipio_col, equipo_col]).size().reset_index(name='Conteo')
                    group.index = group.index + 1  # Índice desde 1
                    st.dataframe(group, use_container_width=True)
                    st.markdown(f"**Total de registros agrupados:** {group['Conteo'].sum()}")

                    # Gráfico de barras apiladas
                    fig = px.bar(
                        group,
                        x=municipio_col,
                        y='Conteo',
                        color=equipo_col,
                        title=f"Registros por {municipio_col} y {equipo_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Botón para descargar datos agrupados en Excel
                    output = io.BytesIO()
                    group.to_excel(output, index=False)
                    st.download_button(
                        label="Descargar datos agrupados en Excel",
                        data=output.getvalue(),
                        file_name="equipos_por_municipio.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                # Footer con información adicional
                st.markdown("---")
                st.markdown("""
                <div style="text-align: center; color: #666;">
                    <p>Dashboard generado automáticamente | Powered by Streamlit & Plotly</p>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Instrucciones cuando no hay archivo cargado
        st.info("👆 Sube un archivo Excel usando el panel lateral para comenzar el análisis.")
        
        # Ejemplos de lo que puede hacer el dashboard
        st.markdown("""
        ### 🚀 Funcionalidades del Dashboard:
        
        - **📊 Estadísticas Automáticas**: Genera automáticamente estadísticas descriptivas
        - **📈 Visualizaciones Interactivas**: Histogramas, boxplots, gráficos de barras y más
        - **🔍 Análisis de Correlaciones**: Matriz de correlación con mapa de calor
        - **⏰ Series de Tiempo**: Detección automática de columnas de fecha
        - **🎯 Análisis Personalizado**: Crea tus propios gráficos de dispersión
        - **📋 Vista de Datos**: Explora y filtra tus datos interactivamente
        
        ### 📋 Formatos Soportados:
        - **.xlsx** (Excel moderno)
        - **.xls** (Excel clásico)
        """)

if __name__ == "__main__":
    main()