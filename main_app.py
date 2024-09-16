import streamlit as st
import datetime as dt
import pandas as pd

class Investimento:
    """Classe base para representar um investimento."""

    def __init__(self, investimento_inicial, vencimento_ano):
        self.investimento_inicial = investimento_inicial
        self.vencimento_ano = vencimento_ano
        self.ano_atual = dt.datetime.now().year
        self.periodo_anos = self.vencimento_ano - self.ano_atual
        self.periodo_meses = self.periodo_anos * 12

    def calcular_aliquota_ir(self, meses):
        """Calcula a alíquota de IR com base no tempo de investimento."""
        if meses <= 6:
            return 0.225
        elif meses <= 12:
            return 0.20
        elif meses <= 24:
            return 0.175
        else:
            return 0.15

    def calcular_rentabilidade(self, taxa_anual, tipo_juros="composto", cupom_mensal=False, tem_ir=True):
        """
        Calcula a rentabilidade do investimento.

        Args:
            taxa_anual (float): Taxa de juros anual.
            tipo_juros (str, optional): Tipo de juros ("simples" ou "composto"). Defaults to "composto".
            cupom_mensal (bool, optional): True se houver pagamento de cupom mensal, False caso contrário. Defaults to False.
            tem_ir (bool, optional): True se houver incidência de IR, False caso contrário. Defaults to True.

        Returns:
            dict: Um dicionário contendo a rentabilidade líquida (valor) e a porcentagem de rentabilidade.
        """
        if cupom_mensal:
            rentabilidade_liquida_total = 0
            for mes in range(1, self.periodo_meses + 1):
                aliquota_ir = self.calcular_aliquota_ir(mes)
                rentabilidade_liquida_mensal = taxa_anual / 12 * (1 - aliquota_ir)
                rentabilidade_liquida_total += self.investimento_inicial * rentabilidade_liquida_mensal
            rentabilidade_liquida = rentabilidade_liquida_total
        else:
            if tipo_juros == "composto":
                rentabilidade_bruta = (self.investimento_inicial * (1 + taxa_anual) ** self.periodo_anos) - self.investimento_inicial
            else:  # tipo_juros == "simples"
                rentabilidade_bruta = self.investimento_inicial * taxa_anual * self.periodo_anos

            if tem_ir:
                aliquota_ir = self.calcular_aliquota_ir(self.periodo_meses)
                rentabilidade_liquida = rentabilidade_bruta * (1 - aliquota_ir)
            else:
                rentabilidade_liquida = rentabilidade_bruta

        porcentagem_rentabilidade = (rentabilidade_liquida / self.investimento_inicial) * 100
        return {
            "valor": rentabilidade_liquida,
            "porcentagem": porcentagem_rentabilidade
        }

class InvestimentoPreFixado(Investimento):
    """Classe para representar um investimento pré-fixado."""
    pass

class InvestimentoPosFixado(Investimento):
    """Classe para representar um investimento pós-fixado."""
    def calcular_rentabilidade(self, taxa_anual, tipo_juros="composto", cupom_mensal=False, tem_ir=True):
        """
        Para investimentos pós-fixados, a taxa_anual recebida já deve ser a taxa efetiva,
        calculada com base no CDI e no percentual do CDI do investimento.
        """
        return super().calcular_rentabilidade(taxa_anual, tipo_juros, cupom_mensal, tem_ir)

class InvestimentoInflacao(Investimento):
    """Classe para representar um investimento indexado à inflação."""
    def calcular_rentabilidade(self, taxa_anual, tipo_juros="composto", cupom_mensal=False, tem_ir=True):
        """
        Para investimentos indexados à inflação, a taxa_anual recebida já deve ser a taxa efetiva,
        calculada com base na inflação e na taxa do investimento.
        """
        return super().calcular_rentabilidade(taxa_anual, tipo_juros, cupom_mensal, tem_ir)

def exibir_resultados(resultados, periodo_anos, investimento_inicial, cupom_mensal_com_ir, cupom_mensal_sem_ir, taxa_com_ir, taxa_sem_ir):
    """Exibe os resultados em um DataFrame."""

    resultados_df = pd.DataFrame({
        "Investimento Inicial": [
            f"R$ {investimento_inicial:,.2f}", 
            f"R$ {investimento_inicial:,.2f}"
        ],
        "Vencimento (anos)": [periodo_anos] * 2,
        "Cupom Mensal": [cupom_mensal_com_ir, cupom_mensal_sem_ir], # Corrigido: usa os valores corretos de cupom mensal
        "Taxa": [f"{taxa_com_ir:.2%}", f"{taxa_sem_ir:.2%}"],
        "Rentabilidade Líquida": [
            f"R$ {resultados['com_ir']['valor']:,.2f}", 
            f"R$ {resultados['sem_ir']['valor']:,.2f}"
        ],
        "Rentabilidade Total (%)": [
            f"{resultados['com_ir']['porcentagem']:.2f}%", 
            f"{resultados['sem_ir']['porcentagem']:.2f}%"
        ]
    }, index=['Com IR', 'Sem IR'])
    st.table(resultados_df)
    return resultados_df 

def exibir_pre_fixado(investimento):
    """Exibe os resultados para investimento pré-fixado."""
    st.title('Pré-fixado')

    with st.form(key='Pre'):
        taxa_com_ir = st.number_input('Taxa com IR (%) (CDB)', value=15.00) / 100
        cupom_mensal_com_ir = st.checkbox('Com Cupom Mensal', value=False, key='cupom_mensal_com_ir')
        taxa_sem_ir = st.number_input('Taxa sem IR (%) (LCI/ LCA)', value=10.50) / 100
        cupom_mensal_sem_ir = st.checkbox('Com Cupom Mensal?', value=False, key='cupom_mensal_sem_ir')
        st.form_submit_button('Calcular')

    if taxa_com_ir != 0 or taxa_sem_ir != 0:
        resultados = {
            "com_ir": investimento.calcular_rentabilidade(
                taxa_com_ir, cupom_mensal=cupom_mensal_com_ir, tem_ir=True
            ),
            "sem_ir": investimento.calcular_rentabilidade(
                taxa_sem_ir, cupom_mensal=cupom_mensal_sem_ir, tem_ir=False
            )
        }
        return exibir_resultados(resultados, investimento.periodo_anos, investimento.investimento_inicial,
                         cupom_mensal_com_ir, cupom_mensal_sem_ir, taxa_com_ir, taxa_sem_ir)

def exibir_pos_fixado(investimento):
    """Exibe os resultados para investimento pós-fixado."""
    st.title('Pós Fixado')

    with st.form(key='Pos'):
        cdi_anual = st.number_input('CDI Anual (%)', value=11.50) / 100
        percentual_cdi_com_ir = st.number_input('Percentual do CDI com IR (%) (CDB)', value=125.00) / 100
        cupom_mensal_com_ir = st.checkbox('Com Cupom Mensal', value=False, key='cupom_mensal_com_ir_pos')
        percentual_cdi_sem_ir = st.number_input('Percentual do CDI sem IR (%) (LCI/ LCA)', value=95.00) / 100
        cupom_mensal_sem_ir = st.checkbox('Com Cupom Mensal?', value=False, key='cupom_mensal_sem_ir_pos')
        st.form_submit_button('Calcular')

    if cdi_anual != 0 and (percentual_cdi_com_ir != 0 or percentual_cdi_sem_ir != 0):
        taxa_com_ir = cdi_anual * percentual_cdi_com_ir
        taxa_sem_ir = cdi_anual * percentual_cdi_sem_ir
        resultados = {
            "com_ir": investimento.calcular_rentabilidade(
                taxa_com_ir, cupom_mensal=cupom_mensal_com_ir, tem_ir=True
            ),
            "sem_ir": investimento.calcular_rentabilidade(
                taxa_sem_ir, cupom_mensal=cupom_mensal_sem_ir, tem_ir=False
            )
        }
        return exibir_resultados(resultados, investimento.periodo_anos, investimento.investimento_inicial, 
                         cupom_mensal_com_ir, cupom_mensal_sem_ir, taxa_com_ir, taxa_sem_ir)

def exibir_inflacao(investimento):
    """Exibe os resultados para investimento indexado à inflação."""
    st.title('Inflação')

    with st.form(key='Inf'):
        inflacao_anual = st.number_input('Inflação Anual (%)', value=4.50) / 100
        taxa_com_ir = st.number_input('Taxa com IR (%) (CDB)', value=6.80) / 100
        cupom_mensal_com_ir = st.checkbox('Com Cupom Mensal', value=False, key='cupom_mensal_com_ir_inf')
        taxa_sem_ir = st.number_input('Taxa sem IR (%) (LCI/ LCA)', value=5.30) / 100
        cupom_mensal_sem_ir = st.checkbox('Com Cupom Mensal?', value=False, key='cupom_mensal_sem_ir_inf')
        st.form_submit_button('Calcular')

    if inflacao_anual != 0 and (taxa_com_ir != 0 or taxa_sem_ir != 0):
        taxa_efetiva_com_ir = inflacao_anual + taxa_com_ir
        taxa_efetiva_sem_ir = inflacao_anual + taxa_sem_ir

        resultados = {
            "com_ir": investimento.calcular_rentabilidade(
                taxa_efetiva_com_ir, cupom_mensal=cupom_mensal_com_ir, tem_ir=True
            ),
            "sem_ir": investimento.calcular_rentabilidade(
                taxa_efetiva_sem_ir, cupom_mensal=cupom_mensal_sem_ir, tem_ir=False
            )
        }
        return exibir_resultados(resultados, investimento.periodo_anos, investimento.investimento_inicial, 
                         cupom_mensal_com_ir, cupom_mensal_sem_ir, taxa_com_ir, taxa_sem_ir)

def exibir_resumo(resultados_investimentos):
    """Exibe um resumo dos investimentos."""
    st.title('Resumo')

    if resultados_investimentos:
        resumo_data = []
        for tipo_investimento, df in resultados_investimentos.items():
            for index, row in df.iterrows():
                resumo_data.append([
                    tipo_investimento,
                    row['Investimento Inicial'],
                    row['Vencimento'],
                    row['Cupom Mensal'],
                    row['Taxa'],
                    row['Rentabilidade Líquida'],
                    row['Rentabilidade Total (%)']
                ])

        resumo_df = pd.DataFrame(resumo_data, columns=[
            "Tipo de Investimento", 
            "Investimento Inicial", 
            "Vencimento", 
            "Cupom Mensal", 
            "Taxa",
            "Rentabilidade Líquida",
            "Rentabilidade Total (%)"
        ])
        st.table(resumo_df)
    else:
        st.write("Nenhum resultado de investimento disponível.")

# Função principal da aplicação
def main():
    """Função principal que gerencia a aplicação."""
    st.sidebar.title('Comparador de Renda Fixa')
    st.sidebar.markdown('---')
    st.sidebar.subheader('Dados de Entrada')
    investimento_inicial = st.sidebar.number_input('Valor Investido', value=50000)
    vencimento_ano = st.sidebar.number_input('Ano de Vencimento', value=2026)
    st.sidebar.markdown('---')

    lista_menu = ['Pré-fixado', 'Pós Fixado', 'Inflação', 'Resumo']
    escolha = st.sidebar.radio('Escolha a opção', lista_menu)

    # Dicionário para armazenar os resultados dos investimentos, agora com DataFrames
    resultados_investimentos = {} 

    # Criar as instâncias das classes de investimento fora do if/else
    investimento_pre = InvestimentoPreFixado(investimento_inicial, vencimento_ano)
    investimento_pos = InvestimentoPosFixado(investimento_inicial, vencimento_ano)
    investimento_inf = InvestimentoInflacao(investimento_inicial, vencimento_ano)

    if escolha == 'Pré-fixado':
        resultados_investimentos["Pré-fixado"] = exibir_pre_fixado(investimento_pre)
    elif escolha == 'Pós Fixado':
        resultados_investimentos["Pós Fixado"] = exibir_pos_fixado(investimento_pos)
    elif escolha == 'Inflação':
        resultados_investimentos["Inflação"] = exibir_inflacao(investimento_inf)
    elif escolha == 'Resumo':
        exibir_resumo(resultados_investimentos)

# Inicia a aplicação
if __name__ == '__main__':
    main()