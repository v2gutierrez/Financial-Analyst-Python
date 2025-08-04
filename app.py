import streamlit as st
import yfinance as yf
import pandas as pd

# --- Configuración de la página ---
st.set_page_config(
    page_title="Análisis Financiero de Empresas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Funciones de soporte (las que ya creamos) ---

def obtener_datos_financieros(ticker_symbol):
    """Descarga los datos financieros de un ticker usando yfinance."""
    try:
        empresa = yf.Ticker(ticker_symbol)
        balance = empresa.balance_sheet
        financials = empresa.financials
        return balance, financials
    except Exception as e:
        st.error(f"No se pudieron obtener los datos para {ticker_symbol}. Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

def aplanar_dataframe(df):
    """Aplanar el MultiIndex y limpiar los DataFrames de yfinance."""
    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index(level=1, drop=True)
    df.columns = df.columns.astype(str)
    return df

# --- Datos de ejemplo de empresas (reemplaza esto con una fuente real) ---
COMPANIES_DATA = {
    "España": {
        "IBEX 35": [
            {"name": "Inditex", "ticker": "ITX.MC"},
            {"name": "Banco Santander", "ticker": "SAN.MC"},
            {"name": "BBVA", "ticker": "BBVA.MC"},
        ],
        "Otros": [
            {"name": "Telefónica", "ticker": "TEF.MC"},
        ],
    },
    "USA": {
        "S&P 500": [
            {"name": "Apple", "ticker": "AAPL"},
            {"name": "Microsoft", "ticker": "MSFT"},
            {"name": "Google", "ticker": "GOOG"},
        ]
    }
}

# --- Lógica de la aplicación con Streamlit ---

st.title("📊 Comparador de Datos Financieros")
st.markdown("Usa los filtros del menú lateral para seleccionar empresas y comparar sus datos financieros.")

# --- Barra lateral para filtros ---
st.sidebar.header("Filtros")

# Selectores de país, mercado y empresa
pais = st.sidebar.selectbox("Selecciona un país:", list(COMPANIES_DATA.keys()))
mercado = st.sidebar.selectbox("Selecciona un mercado:", list(COMPANIES_DATA[pais].keys()))

# Obtener la lista de empresas para el mercado seleccionado
empresas_disponibles = COMPANIES_DATA[pais][mercado]
opciones_empresas = {empresa['name']: empresa['ticker'] for empresa in empresas_disponibles}

# Selector de empresas
empresas_seleccionadas_nombres = st.sidebar.multiselect(
    "Selecciona una o más empresas:",
    list(opciones_empresas.keys())
)

# Botón para iniciar el análisis
if st.sidebar.button("Analizar empresas"):
    if not empresas_seleccionadas_nombres:
        st.warning("Por favor, selecciona al menos una empresa.")
    else:
        st.header("Resultados del Análisis")

        if len(empresas_seleccionadas_nombres) > 1:
            # --- Comparación de múltiples empresas ---
            st.subheader("Comparación de Empresas")
            comparacion_balances = {}
            comparacion_resultados = {}

            for nombre_empresa in empresas_seleccionadas_nombres:
                ticker = opciones_empresas[nombre_empresa]
                balance, financials = obtener_datos_financieros(ticker)
                
                if not balance.empty and not financials.empty:
                    comparacion_balances[nombre_empresa] = aplanar_dataframe(balance)
                    comparacion_resultados[nombre_empresa] = aplanar_dataframe(financials)

            # Muestra las tablas de comparación
            if comparacion_balances:
                st.markdown("### Balances Comparados")
                for nombre, df in comparacion_balances.items():
                    st.markdown(f"#### {nombre}")
                    st.dataframe(df)

            if comparacion_resultados:
                st.markdown("### Cuentas de Resultados Comparadas")
                for nombre, df in comparacion_resultados.items():
                    st.markdown(f"#### {nombre}")
                    st.dataframe(df)

        else:
            # --- Análisis de una sola empresa y su historial ---
            nombre_empresa = empresas_seleccionadas_nombres[0]
            ticker = opciones_empresas[nombre_empresa]
            st.subheader(f"Análisis Histórico de {nombre_empresa} ({ticker})")

            balance, financials = obtener_datos_financieros(ticker)
            
            if not balance.empty:
                st.markdown("### Balance Histórico")
                st.dataframe(aplanar_dataframe(balance))

            if not financials.empty:
                st.markdown("### Cuenta de Resultados Histórica")
                st.dataframe(aplanar_dataframe(financials))