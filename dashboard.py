import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Empresa", layout="wide")
st.title("Dashboard Dinámico de Acciones Empresariales")

# Nombre del archivo Excel por defecto
EXCEL_DEFAULT = "MATRIZ BENEFICIARIOS.xlsx"

# Paletas de colores de tu empresa
colores_empresa = ["#9F2241", "#965F36", "#BC955B", "#DDC8A4"]
degradado_rojo_cafe = [
    "#9F2241", "#A63A4B", "#AD5265", "#B46A7F", "#BC8299", "#965F36"
]

# Estado de sesión para saber si hay archivo cargado
if "archivo_cargado" not in st.session_state:
    if os.path.exists(EXCEL_DEFAULT):
        st.session_state.archivo_cargado = EXCEL_DEFAULT
    else:
        st.session_state.archivo_cargado = None

# Botón de salir (solo si hay archivo cargado)
if st.session_state.archivo_cargado:
    if st.button("Salir y cargar otro Excel"):
        st.session_state.archivo_cargado = None
        st.experimental_rerun()

# Si no hay archivo cargado, muestra el uploader
if not st.session_state.archivo_cargado:
    uploaded_file = st.file_uploader("Carga el archivo Excel", type=["xlsx", "xls"])
    if uploaded_file:
        with open(EXCEL_DEFAULT, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state.archivo_cargado = EXCEL_DEFAULT
        st.experimental_rerun()
else:
    # Carga el archivo Excel
    df = pd.read_excel(st.session_state.archivo_cargado)
    df["ROI ARTESANADO"] = pd.to_numeric(df["ROI ARTESANADO"], errors="coerce")
    df["MONTO INVERSIÓN"] = pd.to_numeric(df["MONTO INVERSIÓN"], errors="coerce")
    df["BENEFICIARIOS"] = pd.to_numeric(df["BENEFICIARIOS"], errors="coerce")

    # Asegúrate de que la columna de año se llame "AÑO"
    if "AÑO" not in df.columns:
        st.error("El archivo Excel debe tener una columna llamada 'AÑO'.")
        st.stop()

    anios = sorted(df["AÑO"].dropna().unique())
    anio_tabs = st.tabs([str(a) for a in anios])

    for idx, anio in enumerate(anios):
        with anio_tabs[idx]:
            st.subheader(f"Estadísticas para el año {anio}")
            df_anio = df[df["AÑO"] == anio]

            tabs = st.tabs(["Vista General IIFAEM", "Vista por Municipio"])

            # Vista General
            with tabs[0]:
                st.header("Analítica General IIFAEM")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Municipios", df_anio["MUNICIPIO"].nunique())
                col2.metric("Total Acciones", len(df_anio))
                col3.metric("Total Beneficiarios", int(df_anio["BENEFICIARIOS"].sum()))
                col4.metric("Monto Total Inversión", f"${df_anio['MONTO INVERSIÓN'].sum():,.2f}")

                st.subheader("Acciones por Municipio")
                fig1 = px.bar(
                    df_anio.groupby("MUNICIPIO")["BENEFICIARIOS"].sum().reset_index(),
                    x="MUNICIPIO", y="BENEFICIARIOS",
                    color="BENEFICIARIOS", color_continuous_scale=degradado_rojo_cafe,
                    title="Beneficiarios por Municipio",
                    text="BENEFICIARIOS"
                )
                fig1.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig1, use_container_width=True)

                st.subheader("Inversión por Acción")
                fig2 = px.pie(
                    df_anio.groupby("OBRA/ACCIÓN")["MONTO INVERSIÓN"].sum().reset_index(),
                    names="OBRA/ACCIÓN", values="MONTO INVERSIÓN",
                    title="Distribución de Inversión por Acción",
                    color_discrete_sequence=colores_empresa
                )
                st.plotly_chart(fig2, use_container_width=True)

                st.subheader("Beneficiarios por Acción")
                fig2b = px.bar(
                    df_anio.groupby("OBRA/ACCIÓN")["BENEFICIARIOS"].sum().reset_index(),
                    x="OBRA/ACCIÓN", y="BENEFICIARIOS",
                    color="BENEFICIARIOS", color_continuous_scale=degradado_rojo_cafe,
                    title="Beneficiarios por Acción",
                    text="BENEFICIARIOS"
                )
                fig2b.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig2b, use_container_width=True)

                st.subheader("ROI Promedio por Municipio")
                fig3 = px.bar(
                    df_anio.groupby("MUNICIPIO")["ROI ARTESANADO"].mean().reset_index(),
                    x="MUNICIPIO", y="ROI ARTESANADO",
                    color="ROI ARTESANADO", color_continuous_scale=degradado_rojo_cafe,
                    title="ROI Promedio por Municipio",
                    text="ROI ARTESANADO"
                )
                fig3.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                st.plotly_chart(fig3, use_container_width=True)

                st.subheader("Tabla General")
                st.dataframe(df_anio)

            # Vista por Municipio
            with tabs[1]:
                st.header("Analítica por Municipio")
                municipios = df_anio["MUNICIPIO"].unique()
                municipio_sel = st.selectbox("Selecciona un municipio", municipios, key=f"municipio_{anio}")
                acciones = df_anio["OBRA/ACCIÓN"].unique()
                accion_sel = st.multiselect("Filtra por acción", acciones, default=list(acciones), key=f"accion_{anio}")

                df_filtrado = df_anio[(df_anio["MUNICIPIO"] == municipio_sel) & (df_anio["OBRA/ACCIÓN"].isin(accion_sel))]

                st.subheader(f"Resumen para {municipio_sel}")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Acciones", len(df_filtrado))
                col2.metric("Total Beneficiarios", int(df_filtrado["BENEFICIARIOS"].sum()))
                col3.metric("Monto Total Inversión", f"${df_filtrado['MONTO INVERSIÓN'].sum():,.2f}")
                col4.metric("ROI Promedio Artesanado", f"{df_filtrado['ROI ARTESANADO'].mean():.2f}")

                st.subheader("Acciones por Categoría")
                fig4 = px.bar(
                    df_filtrado.groupby("OBRA/ACCIÓN")["BENEFICIARIOS"].sum().reset_index(),
                    x="OBRA/ACCIÓN", y="BENEFICIARIOS",
                    color="BENEFICIARIOS", color_continuous_scale=degradado_rojo_cafe,
                    title="Beneficiarios por Acción",
                    text="BENEFICIARIOS"
                )
                fig4.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig4, use_container_width=True)

                st.subheader("Inversión por Acción")
                fig5 = px.bar(
                    df_filtrado.groupby("OBRA/ACCIÓN")["MONTO INVERSIÓN"].sum().reset_index(),
                    x="OBRA/ACCIÓN", y="MONTO INVERSIÓN",
                    color="MONTO INVERSIÓN", color_continuous_scale=colores_empresa,
                    title="Inversión por Acción",
                    text="MONTO INVERSIÓN"
                )
                fig5.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
                st.plotly_chart(fig5, use_container_width=True)

                st.subheader("ROI por Acción")
                fig6 = px.bar(
                    df_filtrado.groupby("OBRA/ACCIÓN")["ROI ARTESANADO"].mean().reset_index(),
                    x="OBRA/ACCIÓN", y="ROI ARTESANADO",
                    color="ROI ARTESANADO", color_continuous_scale=degradado_rojo_cafe,
                    title="ROI Promedio por Acción",
                    text="ROI ARTESANADO"
                )
                fig6.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                st.plotly_chart(fig6, use_container_width=True)

                st.subheader("Tabla Detallada")
                st.dataframe(df_filtrado)

st.stop()