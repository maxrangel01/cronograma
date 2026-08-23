import pandas as pd
import datetime
import streamlit as st
import sqlite3
import warnings
import plotly.express as px
warnings.filterwarnings('ignore')

banco = sqlite3.connect('banco.db')
banco.execute('''CREATE TABLE IF NOT EXISTS projeto (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Material TEXT,
    ITEM TEXT,
    QTD INTEGER,
    ATIVIDADE TEXT,
    RESPONSAVEIS TEXT,
    INICIO DATE,
    DURACAO INTEGER,
    TERMINO DATE,
    OBS TEXT    
)''')

def salvar(Material,ITEM,QTD,ATIVIDADE,RESPONSAVEIS,INICIO,DURACAO,TERMINO,OBS):    
    banco.execute("INSERT INTO projeto (Material, ITEM, QTD, ATIVIDADE, RESPONSAVEIS, INICIO, DURACAO, TERMINO, OBS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (Material, ITEM, QTD, ATIVIDADE, RESPONSAVEIS, INICIO, DURACAO, TERMINO, OBS))
    banco.commit()
    return banco

def carregar():
    planilha = pd.read_sql_query("SELECT * FROM projeto", banco,index_col='ID')
    return planilha

def excluir(id):
    banco.execute("DELETE FROM projeto WHERE ID = ?", (id,))
    banco.commit()
    return banco

def editar(ID, Material, ITEM, QTD, ATIVIDADE, RESPONSAVEIS, INICIO, DURACAO, TERMINO, OBS):
    banco.execute("UPDATE projeto SET Material = ?, ITEM = ?, QTD = ?, ATIVIDADE = ?, RESPONSAVEIS = ?, INICIO = ?, DURACAO = ?, TERMINO = ?, OBS = ? WHERE ID = ?", (Material, ITEM, QTD, ATIVIDADE, RESPONSAVEIS, INICIO, DURACAO, TERMINO, OBS, ID))
    banco.commit()
    return banco



st.set_page_config(page_title="Cronograma de Projeto", page_icon=":hourglass:", layout="wide")
st.title(f"Cronograma de Projeto {datetime.datetime.now().strftime('%d/%m/%Y')}")
st.subheader(":hourglass: Sistema de Controle de Cronograma de Projeto")


planilha = pd.read_sql_query("SELECT * FROM projeto", banco,index_col='ID')

coluna1,coluna2 = st.columns((2))


st.sidebar.header("Filtros_de_Atividade")
filtro_atividade = st.sidebar.multiselect("Selecione a Atividade", planilha['ATIVIDADE'].unique())
if filtro_atividade:
    planilha = planilha[planilha['ATIVIDADE'].isin(filtro_atividade)]
filtro_responsavel = st.sidebar.multiselect("Selecione o Responsável", planilha['RESPONSAVEIS'].unique())
if filtro_responsavel:
    planilha = planilha[planilha['RESPONSAVEIS'].isin(filtro_responsavel)] 
if filtro_atividade and filtro_responsavel:
    planilha = planilha[(planilha['ATIVIDADE'].isin(filtro_atividade)) & (planilha['RESPONSAVEIS'].isin(filtro_responsavel))]


with coluna1:
    
    Material = st.text_input("Digite o material").upper()
    ITEM = st.text_input("Digite o item").upper()   
    QTD = int(st.number_input("Digite a quantidade", min_value=0, value=0))
    ATIVIDADE = st.selectbox("Digite a atividade",['MONTAGEM','JATEAMENTO','TESTE','PINTURA','OUTROS'])
    RESPONSAVEIS = st.selectbox("Digite o responsável", ['JOAO','MARIA','PEDRO','ANA','OUTROS'])
    INICIO = st.date_input("Digite a data inicial")
    DURACAO = int(st.number_input("Digite a duração em dias", min_value=0, value=0))
    TERMINO = st.date_input("Digite a data final", value=INICIO + datetime.timedelta(days=DURACAO))
    OBS = st.text_input("Digite a observação").upper()
    if st.button("Salvar"):
        salvar(Material,ITEM,QTD,ATIVIDADE,RESPONSAVEIS,INICIO,DURACAO,TERMINO,OBS)
        st.success("Atividade salva com sucesso!")
        carregar()
    texto_editar = st.number_input("Digite o ID que deseja editar", min_value=0, value=0)
    if st.button("Editar"):
        editar(texto_editar, Material, ITEM, QTD, ATIVIDADE, RESPONSAVEIS, INICIO, DURACAO, TERMINO, OBS)
        st.success("Atividade editada com sucesso!")
        carregar()
with coluna2:
    st.subheader("itens do Projeto")
    st.dataframe(planilha)
    texto_excluir = st.text_input("Digite o iD que deseja excluir")
    
    if st.button("Excluir"):        
        excluir(texto_excluir)
        st.success("Atividade excluída com sucesso!")
        carregar()
    

with st.expander("Visualização do Cronograma"):
    if filtro_atividade:
        planilha_filtrada = planilha[planilha['ATIVIDADE'].isin(filtro_atividade)]
    else:
        planilha_filtrada = planilha.copy()
    
    fig = px.timeline(planilha_filtrada, x_start="INICIO", x_end="TERMINO", y="ATIVIDADE", color="RESPONSAVEIS", hover_data=["Material", "ITEM", "QTD", "OBS"])
    fig.update_yaxes(autorange="reversed")  # Inverte a ordem do eixo y
    st.plotly_chart(fig, use_container_width=True)



