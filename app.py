# Importando bibliotecas
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] == st.secrets["passwords"]['username'] and st.session_state["password"] == st.secrets["passwords"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )


        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

    # Configurações do Streamlit
    st.set_page_config(page_title='Análise de Processos', layout='wide')

    # Carregar dados
    @st.cache
    def load_data():
        df = pd.read_excel('Processos (exportar para excel) (36).xls', sheet_name='Relatório')
        df['Data da distribuição'] = pd.to_datetime(df['Data da distribuição'])
        df['Semestre da distribuição'] = df['Data da distribuição'].dt.to_period('M').dt.to_timestamp().dt.to_period('2M')
        return df

    df = load_data()

    # Título
    st.title('Análise de Processos')

    # Sidebar com filtros
    st.sidebar.header('Filtros')

    # Filtrar por UF, Cidade, Tipo, Responsável, Órgão, e Cliente Principal usando dropdowns com seleção única
    uf_selected = st.sidebar.selectbox('UF', options=['Todos'] + list(df['UF'].unique()), format_func=lambda x: x if x else 'N/A')
    city_selected = st.sidebar.selectbox('Cidade', options=['Todos'] + list(df['Cidade'].unique()), format_func=lambda x: x if x else 'N/A')
    type_selected = st.sidebar.selectbox('Tipo', options=['Todos'] + list(df['Tipo'].unique()), format_func=lambda x: x if x else 'N/A')
    responsible_selected = st.sidebar.selectbox('Responsável Principal', options=['Todos'] + list(df['Responsável principal'].unique()), format_func=lambda x: x if x else 'N/A')
    org_selected = st.sidebar.selectbox('Órgão', options=['Todos'] + list(df['Órgão'].unique()), format_func=lambda x: x if x else 'N/A')
    client_selected = st.sidebar.selectbox('Cliente Principal', options=['Todos'] + list(df['Cliente principal'].unique()), format_func=lambda x: x if x else 'N/A')

    # Aplicando filtros
    df_filtered = df[(df['UF'] == uf_selected) if uf_selected != 'Todos' else df['UF'].notnull()]
    df_filtered = df_filtered[(df_filtered['Cidade'] == city_selected) if city_selected != 'Todos' else df_filtered['Cidade'].notnull()]
    df_filtered = df_filtered[(df_filtered['Tipo'] == type_selected) if type_selected != 'Todos' else df_filtered['Tipo'].notnull()]
    df_filtered = df_filtered[(df_filtered['Responsável principal'] == responsible_selected) if responsible_selected != 'Todos' else df_filtered['Responsável principal'].notnull()]
    df_filtered = df_filtered[(df_filtered['Órgão'] == org_selected) if org_selected != 'Todos' else df_filtered['Órgão'].notnull()]
    df_filtered = df_filtered[(df_filtered['Cliente principal'] == client_selected) if client_selected != 'Todos' else df_filtered['Cliente principal'].notnull()]

    # Seção de visualizações
    st.header('Visualizações')

    # Função para criar os gráficos
    def plot_countplot(df, column, title, top_n=None, rotation=0):
        top_categories = df[column].value_counts().nlargest(top_n).index.tolist() if top_n else df[column].unique()
        df_top_categories = df[df[column].isin(top_categories)]
        if len(df_top_categories[column].unique()) > 1:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.countplot(data=df_top_categories, x=column, ax=ax, order=df_top_categories[column].value_counts().index)
            plt.xticks(rotation=rotation)
            plt.title(title)
            st.pyplot(fig)
        else:
            st.write(f'Não há dados suficientes para mostrar o gráfico de {title.lower()}.')

    # Visualizações mostrando apenas os mais frequentes (Top 10)
    plot_countplot(df_filtered, 'Ação', '1. Distribuição dos processos por Tipo de Ação', top_n=10, rotation=45)
    plot_countplot(df_filtered, 'UF', '2. Distribuição dos Processos por UF', top_n=10)
    plot_countplot(df_filtered, 'Responsável principal', '4. Distribuição dos Processos por Responsável Principal', top_n=10, rotation=45)
    plot_countplot(df_filtered, 'Cliente principal', '6. Distribuição dos Processos por Cliente Principal', top_n=10, rotation=45)
    plot_countplot(df_filtered, 'Posição do cliente', '7. Distribuição dos Processos por Posição do Cliente', top_n=10, rotation=45)
    plot_countplot(df_filtered, 'Tipo', '8. Distribuição dos Processos por Tipo', top_n=10)
    plot_countplot(df_filtered, 'Vara/turma', '9. Distribuição dos Processos por Vara/Turma', top_n=10, rotation=45)
    plot_countplot(df_filtered, 'Órgão', '10. Distribuição dos Processos por Órgão', top_n=10, rotation=45)

