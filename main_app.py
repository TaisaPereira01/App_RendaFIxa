import streamlit as st
import pandas as pd
import datetime as dt
#import numpy as np

# Calcula o juros simples para retorno do investimento
def calcular_juros_simples(investimento_inicial, taxa_anual, periodo_anos):
    rentabilidade_bruta = investimento_inicial * taxa_anual * periodo_anos
    return rentabilidade_bruta

# Calcula o juros composto para retorno do investimento
def calcular_juros_compostos(investimento_inicial, taxa_anual, periodo_anos):
    montante = investimento_inicial * (1 + taxa_anual) ** periodo_anos    
    rentabilidade_bruta = montante - investimento_inicial    
    return rentabilidade_bruta

# Função para calcular a rentabilidade líquida anual com juros simples
def calcular_rentabilidade_liquida_anual(taxa_anual, aliquota_ir, meses):
    taxa_mensal = taxa_anual / 12
    rendimento_liquido_mensal = taxa_mensal * (1 - aliquota_ir)
    #rentabilidade_anual = (1 + rendimento_liquido_mensal) ** meses - 1
    rentabilidade_anual = rendimento_liquido_mensal * meses
    return rentabilidade_anual

# Função para gerar a lista da quantidade de meses para calculo da aliquota de IR
def Lista_Periodos_ir(total_meses):
    # Verificando se o valor total é maior ou igual a 0
    if total_meses < 0:
        return "O valor deve ser maior ou igual a 0."
    # Distribuindo o valor nos elementos da lista
    elementos = [min(6, total_meses)]  # Elemento 1 (máximo 6)
    total_meses -= elementos[0]
    elementos.append(min(6, total_meses))  # Elemento 2 (máximo 6)
    total_meses -= elementos[1]
    elementos.append(min(12, total_meses))  # Elemento 3 (máximo 12)
    total_meses -= elementos[2]
    elementos.append(total_meses)  # Elemento 4 (restante)
    return elementos

# Calcula a aliquota de IR que será aplicada no investimento
def calcular_aliquota_ir(meses):
    if meses <= 6:
        return 22.5/100
    elif meses <= 12:
        return 20.0/100
    elif meses <= 24:
        return 17.5/100
    else:
        return 15.0/100

def pre():
    st.title('Pré-fixado')
    with st.form(key='Pre'):
        Inp_pre_taxa_com_ir=st.number_input('Taxa com IR (%) (CDB)',value=15.00) / 100
        checkbox_cupom_taxa_com_ir=st.checkbox('Com Cupom Mensal',value=False,key='Inp_pre_taxa_com_ir')
        Inp_pre_taxa_sem_ir=st.number_input('Taxa sem IR (%) (LCI/ LCA)',value=10.5) / 100
        checkbox_cupom_taxa_sem_ir=st.checkbox('Com Cupom Mensal?',value=False,key='Inp_pre_taxa_sem_ir')
        st.form_submit_button('Calcular')        
    rentabilidade_bruta=0.0
    rentabilidade_liquida=0.0    
    ano_atual = dt.datetime.now().year
    periodo_anos = vencimento_ano - ano_atual
    periodo_meses = periodo_anos * 12
    aliquotas_ir = [0.225, 0.20, 0.175, 0.15]
    periodos_ir = Lista_Periodos_ir(periodo_meses)
    ir_percent=calcular_aliquota_ir(periodo_meses)
    #st.write('lista periodos: ',periodos_ir)

    # Cálculo da rentabilidade para produtos COM IR
    if Inp_pre_taxa_com_ir != 0 and not checkbox_cupom_taxa_com_ir:        
        rentabilidade_bruta = calcular_juros_compostos(investimento_inicial,Inp_pre_taxa_com_ir,periodo_anos)
        rentabilidade_liquida = rentabilidade_bruta * (1 - ir_percent)
        st.write('Rentabilidade Líquida COM IR: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')

    # Cálculo da rentabilidade COM IR e com flag Cupom Mensal (juros simples)
    else:
        rentabilidade_bruta = 1
        for aliquota, periodo in zip(aliquotas_ir, periodos_ir):
            rentabilidade_bruta *= (1 + calcular_rentabilidade_liquida_anual(Inp_pre_taxa_com_ir,aliquota,periodo))
        rentabilidade_bruta -= 1        
        rentabilidade_liquida = investimento_inicial * (1 + rentabilidade_bruta)
        rentabilidade_liquida = rentabilidade_liquida - investimento_inicial
        st.write('Rentabilidade Líquida COM IR com Cupom Mensal: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')
    
    # Cálculo da rentabilidade para produtos SEM IR    
    if Inp_pre_taxa_sem_ir != 0 and not checkbox_cupom_taxa_sem_ir:        
        rentabilidade_bruta = calcular_juros_compostos(investimento_inicial,Inp_pre_taxa_sem_ir,periodo_anos)
        rentabilidade_liquida = rentabilidade_bruta
        st.write('Rentabilidade Líquida SEM IR: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')
    
    # Cálculo da rentabilidade SEM IR e com flag Cupom Mensal (juros simples)
    else:
        rentabilidade_bruta = calcular_juros_simples(investimento_inicial,Inp_pre_taxa_sem_ir,periodo_anos)        
        rentabilidade_liquida = rentabilidade_bruta
        st.write('Rentabilidade Líquida SEM IR com Cupom Mensal: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')


def pos():
    st.title('Pós Fixado')
    with st.form(key='Pos'):
        Inp_pos_cdi_anual=st.number_input('CDI Anual (%)',value=11.5) / 100    
        Inp_pos_taxa_com_ir=st.number_input('Taxa com IR (%) (CDB)',value=125) / 100
        checkbox_cupom_taxa_com_ir=st.checkbox('Com Cupom Mensal',value=False,key='Inp_pos_taxa_com_ir')
        Inp_pos_taxa_sem_ir=st.number_input('Taxa sem IR (%) (LCI/ LCA)',value=95) / 100
        checkbox_cupom_taxa_sem_ir=st.checkbox('Com Cupom Mensal',value=False,key='Inp_pos_taxa_sem_ir')
        st.form_submit_button('Calcular')
    rentabilidade_bruta=0.0
    rentabilidade_liquida=0.0
    ano_atual = dt.datetime.now().year
    periodo_anos = vencimento_ano - ano_atual
    periodo_meses = periodo_anos * 12
    ir_percent = calcular_aliquota_ir(periodo_meses)
    aliquotas_ir = [0.225, 0.20, 0.175, 0.15]
    periodos_ir = Lista_Periodos_ir(periodo_meses)

    # Cálculo da rentabilidade para produtos COM IR
    if Inp_pos_taxa_com_ir != 0 and not checkbox_cupom_taxa_com_ir:
        taxa = Inp_pos_taxa_com_ir * Inp_pos_cdi_anual
        rentabilidade_bruta = calcular_juros_compostos(investimento_inicial,taxa,periodo_anos)
        rentabilidade_liquida = rentabilidade_bruta * (1 - ir_percent)
        st.write('Rentabilidade Líquida COM IR: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')
    
    # Cálculo da rentabilidade COM IR e com flag Cupom Mensal (juros simples)
    else:
        taxa = Inp_pos_taxa_com_ir * Inp_pos_cdi_anual
        rentabilidade_bruta = 1
        for aliquota, periodo in zip(aliquotas_ir, periodos_ir):
            rentabilidade_bruta *= (1 + calcular_rentabilidade_liquida_anual(taxa,aliquota,periodo))
        rentabilidade_bruta -= 1        
        rentabilidade_liquida = investimento_inicial * (1 + rentabilidade_bruta)
        rentabilidade_liquida = rentabilidade_liquida - investimento_inicial
        st.write('Rentabilidade Líquida COM IR com Cupom Mensal: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')

    # Cálculo da rentabilidade para produtos SEM IR
    if Inp_pos_taxa_sem_ir != 0 and not checkbox_cupom_taxa_sem_ir:
        taxa = Inp_pos_taxa_sem_ir * Inp_pos_cdi_anual
        rentabilidade_bruta = calcular_juros_compostos(investimento_inicial,taxa,periodo_anos)
        rentabilidade_liquida = rentabilidade_bruta
        st.write('Rentabilidade Líquida SEM IR: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')
    
    # Cálculo da rentabilidade SEM IR e com flag Cupom Mensal (juros simples)
    else:
        taxa = Inp_pos_taxa_sem_ir * Inp_pos_cdi_anual
        rentabilidade_bruta = calcular_juros_simples(investimento_inicial,taxa,periodo_anos)
        rentabilidade_liquida = rentabilidade_bruta
        st.write('Rentabilidade Líquida SEM IR com Cupom Mensal: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')

        
def inflacao():
    st.title('Inflação')
    with st.form(key='Pos'):
        Inp_inflacao_taxa_anual=st.number_input('Inflação Anual (%)',value=4.5) / 100
        Inp_inflacao_taxa_com_ir=st.number_input('Taxa com IR (%) (CDB)',value=6.8) / 100
        checkbox_cupom_taxa_com_ir=st.checkbox('Com Cupom Mensal',value=False,key='Inp_inflacao_taxa_com_ir')
        Inp_inflacao_taxa_sem_ir=st.number_input('Taxa sem IR (%) (LCI/ LCA)',value=5.3) / 100
        checkbox_cupom_taxa_sem_ir=st.checkbox('Com Cupom Mensal',value=False,key='Inp_inflacao_taxa_sem_ir')
        st.form_submit_button('Calcular')
    rentabilidade_bruta=0.0
    rentabilidade_liquida=0.0    
    ano_atual = dt.datetime.now().year
    periodo_anos = vencimento_ano - ano_atual
    periodo_meses = periodo_anos * 12
    ir_percent=calcular_aliquota_ir(periodo_meses)
    aliquotas_ir = [0.225, 0.20, 0.175, 0.15]
    periodos_ir = Lista_Periodos_ir(periodo_meses)
    
    # Cálculo da rentabilidade para produtos COM IR
    if Inp_inflacao_taxa_com_ir != 0 and not checkbox_cupom_taxa_com_ir:
        taxa = Inp_inflacao_taxa_com_ir + Inp_inflacao_taxa_anual
        rentabilidade_bruta = calcular_juros_compostos(investimento_inicial,taxa,periodo_anos)
        rentabilidade_liquida = rentabilidade_bruta * (1 - ir_percent)
        st.write('Rentabilidade Líquida COM IR: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')
    
    # Cálculo da rentabilidade COM IR e com flag Cupom Mensal (juros simples)
    else:
        taxa = Inp_inflacao_taxa_com_ir + Inp_inflacao_taxa_anual
        rentabilidade_bruta = 1
        for aliquota, periodo in zip(aliquotas_ir, periodos_ir):
            rentabilidade_bruta *= (1 + calcular_rentabilidade_liquida_anual(taxa,aliquota,periodo))
        rentabilidade_bruta -= 1        
        rentabilidade_liquida = investimento_inicial * (1 + rentabilidade_bruta)
        rentabilidade_liquida = rentabilidade_liquida - investimento_inicial
        st.write('Rentabilidade Líquida COM IR com Cupom Mensal: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')
    
    # Cálculo da rentabilidade para produtos SEM IR
    if Inp_inflacao_taxa_sem_ir != 0 and not checkbox_cupom_taxa_sem_ir:
        taxa = Inp_inflacao_taxa_sem_ir + Inp_inflacao_taxa_anual
        rentabilidade_bruta = calcular_juros_compostos(investimento_inicial,taxa,periodo_anos)
        rentabilidade_liquida = rentabilidade_bruta
        st.write('Rentabilidade Líquida SEM IR: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')
    
    # Cálculo da rentabilidade SEM IR e com flag Cupom Mensal (juros simples)
    else:
        taxa = Inp_inflacao_taxa_sem_ir + Inp_inflacao_taxa_anual
        rentabilidade_bruta = calcular_juros_simples(investimento_inicial,taxa,periodo_anos)
        rentabilidade_liquida = rentabilidade_bruta
        st.write('Rentabilidade Líquida SEM IR com Cupom Mensal: ',f"{rentabilidade_liquida:,.2f}",' em ',periodo_anos,' anos')


def resumo():
    st.title('Resumo')    


# Função principal
def main():
    lista_menu=['Pré-fixado', 'Pós Fixado','Inflação','Resumo']
    escolha = st.sidebar.radio('Escolha a opção', lista_menu)
    
    if escolha == 'Pré-fixado':
        pre()
    if escolha =='Pós Fixado':
        pos()
    if escolha == 'Inflação':
        inflacao()
    if escolha == 'Resumo':
        resumo()

# SideBar
st.sidebar.title('Comparador Renda Fixa')
st.sidebar.markdown('---')
st.sidebar.subheader('Dados de Entrada')
investimento_inicial=st.sidebar.number_input('Valor Investido',value=50000)
vencimento_ano=st.sidebar.number_input('Vencimento',value=2026)
st.sidebar.markdown('---')

main()
