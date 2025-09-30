<<<<<<< HEAD
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Empresa", layout="wide")

st.title("Dashboard Dinámico de Acciones Empresariales")

# Subir el archivo Excel
uploaded_file = st.file_uploader("Carga el archivo Excel", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["ROI ARTESANADO"] = pd.to_numeric(df["ROI ARTESANADO"], errors="coerce")
    df["MONTO INVERSIÓN"] = pd.to_numeric(df["MONTO INVERSIÓN"], errors="coerce")
    df["BENEFICIARIOS"] = pd.to_numeric(df["BENEFICIARIOS"], errors="coerce")

    tabs = st.tabs(["Vista General IIFAEM", "Vista por Municipio"])

    # Vista General
    with tabs[0]:
        st.header("Analítica General IIFAEM")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Municipios", df["MUNICIPIO"].nunique())
        col2.metric("Total Acciones", len(df))
        col3.metric("Total Beneficiarios", int(df["BENEFICIARIOS"].sum()))
        col4.metric("Monto Total Inversión", f"${df['MONTO INVERSIÓN'].sum():,.2f}")

        st.subheader("Acciones por Municipio")
        fig1 = px.bar(
            df.groupby("MUNICIPIO")["BENEFICIARIOS"].sum().reset_index(),
            x="MUNICIPIO", y="BENEFICIARIOS",
            color="BENEFICIARIOS", color_continuous_scale="Blues",
            title="Beneficiarios por Municipio"
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Inversión por Acción")
        fig2 = px.pie(
            df.groupby("OBRA/ACCIÓN")["MONTO INVERSIÓN"].sum().reset_index(),
            names="OBRA/ACCIÓN", values="MONTO INVERSIÓN",
            title="Distribución de Inversión por Acción",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("ROI Promedio por Municipio")
        fig3 = px.bar(
            df.groupby("MUNICIPIO")["ROI ARTESANADO"].mean().reset_index(),
            x="MUNICIPIO", y="ROI ARTESANADO",
            color="ROI ARTESANADO", color_continuous_scale="Viridis",
            title="ROI Promedio por Municipio"
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Tabla General")
        st.dataframe(df)

    # Vista por Municipio
    with tabs[1]:
        st.header("Analítica por Municipio")
        municipios = df["MUNICIPIO"].unique()
        municipio_sel = st.selectbox("Selecciona un municipio", municipios)
        acciones = df["OBRA/ACCIÓN"].unique()
        accion_sel = st.multiselect("Filtra por acción", acciones, default=list(acciones))

        df_filtrado = df[(df["MUNICIPIO"] == municipio_sel) & (df["OBRA/ACCIÓN"].isin(accion_sel))]

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
            color="BENEFICIARIOS", color_continuous_scale="Teal",
            title="Beneficiarios por Acción"
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Inversión por Acción")
        fig5 = px.bar(
            df_filtrado.groupby("OBRA/ACCIÓN")["MONTO INVERSIÓN"].sum().reset_index(),
            x="OBRA/ACCIÓN", y="MONTO INVERSIÓN",
            color="MONTO INVERSIÓN", color_continuous_scale="Oranges",
            title="Inversión por Acción"
        )
        st.plotly_chart(fig5, use_container_width=True)

        st.subheader("ROI por Acción")
        fig6 = px.bar(
            df_filtrado.groupby("OBRA/ACCIÓN")["ROI ARTESANADO"].mean().reset_index(),
            x="OBRA/ACCIÓN", y="ROI ARTESANADO",
            color="ROI ARTESANADO", color_continuous_scale="Purples",
            title="ROI Promedio por Acción"
        )
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("Tabla Detallada")
        st.dataframe(df_filtrado)
else:
=======
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Empresa", layout="wide")

st.title("Dashboard Dinámico de Acciones Empresariales")

# Subir el archivo Excel
uploaded_file = st.file_uploader("Carga el archivo Excel", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["ROI ARTESANADO"] = pd.to_numeric(df["ROI ARTESANADO"], errors="coerce")
    df["MONTO INVERSIÓN"] = pd.to_numeric(df["MONTO INVERSIÓN"], errors="coerce")
    df["BENEFICIARIOS"] = pd.to_numeric(df["BENEFICIARIOS"], errors="coerce")

    tabs = st.tabs(["Vista General IIFAEM", "Vista por Municipio"])

    # Vista General
    with tabs[0]:
        st.header("Analítica General IIFAEM")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Municipios", df["MUNICIPIO"].nunique())
        col2.metric("Total Acciones", len(df))
        col3.metric("Total Beneficiarios", int(df["BENEFICIARIOS"].sum()))
        col4.metric("Monto Total Inversión", f"${df['MONTO INVERSIÓN'].sum():,.2f}")

        st.subheader("Acciones por Municipio")
        fig1 = px.bar(
            df.groupby("MUNICIPIO")["BENEFICIARIOS"].sum().reset_index(),
            x="MUNICIPIO", y="BENEFICIARIOS",
            color="BENEFICIARIOS", color_continuous_scale="Blues",
            title="Beneficiarios por Municipio"
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Inversión por Acción")
        fig2 = px.pie(
            df.groupby("OBRA/ACCIÓN")["MONTO INVERSIÓN"].sum().reset_index(),
            names="OBRA/ACCIÓN", values="MONTO INVERSIÓN",
            title="Distribución de Inversión por Acción",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("ROI Promedio por Municipio")
        fig3 = px.bar(
            df.groupby("MUNICIPIO")["ROI ARTESANADO"].mean().reset_index(),
            x="MUNICIPIO", y="ROI ARTESANADO",
            color="ROI ARTESANADO", color_continuous_scale="Viridis",
            title="ROI Promedio por Municipio"
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Tabla General")
        st.dataframe(df)

    # Vista por Municipio
    with tabs[1]:
        st.header("Analítica por Municipio")
        municipios = df["MUNICIPIO"].unique()
        municipio_sel = st.selectbox("Selecciona un municipio", municipios)
        acciones = df["OBRA/ACCIÓN"].unique()
        accion_sel = st.multiselect("Filtra por acción", acciones, default=list(acciones))

        df_filtrado = df[(df["MUNICIPIO"] == municipio_sel) & (df["OBRA/ACCIÓN"].isin(accion_sel))]

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
            color="BENEFICIARIOS", color_continuous_scale="Teal",
            title="Beneficiarios por Acción"
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Inversión por Acción")
        fig5 = px.bar(
            df_filtrado.groupby("OBRA/ACCIÓN")["MONTO INVERSIÓN"].sum().reset_index(),
            x="OBRA/ACCIÓN", y="MONTO INVERSIÓN",
            color="MONTO INVERSIÓN", color_continuous_scale="Oranges",
            title="Inversión por Acción"
        )
        st.plotly_chart(fig5, use_container_width=True)

        st.subheader("ROI por Acción")
        fig6 = px.bar(
            df_filtrado.groupby("OBRA/ACCIÓN")["ROI ARTESANADO"].mean().reset_index(),
            x="OBRA/ACCIÓN", y="ROI ARTESANADO",
            color="ROI ARTESANADO", color_continuous_scale="Purples",
            title="ROI Promedio por Acción"
        )
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("Tabla Detallada")
        st.dataframe(df_filtrado)
else:
>>>>>>> f56c8ebcd12b60b801ed6eabb286b9fc0aa43588
    st.info("Por favor, carga un archivo Excel para comenzar el análisis.")