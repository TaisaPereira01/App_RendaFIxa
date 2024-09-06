import streamlit as st
import pandas as pd
import datetime as dt

class Investimento:
    """
    Classe base para representar um investimento.
    """

    def __init__(self, investimento_inicial, vencimento_ano):
        self.investimento_inicial = investimento_inicial
        self.vencimento_ano = vencimento_ano
        self.ano_atual = dt.datetime.now().year
        self.periodo_anos = self.vencimento_ano - self.ano_atual
        self.periodo_meses = self.periodo_anos * 12

    def calcular_rentabilidade_bruta(self, *args):
        """Calcula a rentabilidade bruta do investimento.

        Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar este método.")

    def calcular_rentabilidade_liquida(self, *args):
        """Calcula a rentabilidade líquida do investimento.

        Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar este método.")

    def gerar_dataframe_resultados(self):
        """Gera um DataFrame com os resultados do investimento.

        Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar este método.")


class InvestimentoPreFixado(Investimento):
    """
    Classe para representar um investimento pré-fixado.
    """

    def __init__(self, investimento_inicial, vencimento_ano, taxa_com_ir, taxa_sem_ir,
                 cupom_taxa_com_ir=False, cupom_taxa_sem_ir=False):
        super().__init__(investimento_inicial, vencimento_ano)
        self.taxa_com_ir = taxa_com_ir
        self.taxa_sem_ir = taxa_sem_ir
        self.cupom_taxa_com_ir = cupom_taxa_com_ir
        self.cupom_taxa_sem_ir = cupom_taxa_sem_ir

    def calcular_rentabilidade_bruta(self):
        if self.cupom_taxa_com_ir or self.cupom_taxa_sem_ir:
            return self._calcular_rentabilidade_cupom()
        else:
            return self._calcular_rentabilidade_composta()

    def _calcular_rentabilidade_composta(self):
        """Calcula a rentabilidade bruta com juros compostos."""
        rentabilidade_com_ir = self.investimento_inicial * (
            (1 + self.taxa_com_ir) ** self.periodo_anos) - self.investimento_inicial
        rentabilidade_sem_ir = self.investimento_inicial * (
            (1 + self.taxa_sem_ir) ** self.periodo_anos) - self.investimento_inicial
        return rentabilidade_com_ir, rentabilidade_sem_ir

    def _calcular_rentabilidade_cupom(self):
        """Calcula a rentabilidade bruta com cupom mensal (juros simples)."""
        rentabilidade_com_ir = self._calcular_rentabilidade_liquida_cupom(self.taxa_com_ir)
        rentabilidade_sem_ir = self._calcular_rentabilidade_liquida_cupom(self.taxa_sem_ir)
        return rentabilidade_com_ir, rentabilidade_sem_ir

    def _calcular_rentabilidade_liquida_cupom(self, taxa):
        """Calcula a rentabilidade líquida com cupom mensal."""
        rentabilidade_bruta = 1
        for aliquota, periodo in zip(self.aliquotas_ir, self.periodos_ir):
            rentabilidade_bruta *= (
                1 + self._calcular_rentabilidade_liquida_anual(taxa, aliquota, periodo))
        rentabilidade_bruta -= 1
        rentabilidade_liquida = self.investimento_inicial * (1 + rentabilidade_bruta)
        rentabilidade_liquida -= self.investimento_inicial
        return rentabilidade_liquida

    def calcular_rentabilidade_liquida(self):
        rentabilidade_bruta_com_ir, rentabilidade_bruta_sem_ir = self.calcular_rentabilidade_bruta()
        ir_percent = self.calcular_aliquota_ir()
        rentabilidade_liquida_com_ir = rentabilidade_bruta_com_ir * (
            1 - ir_percent) if not self.cupom_taxa_com_ir else rentabilidade_bruta_com_ir
        rentabilidade_liquida_sem_ir = rentabilidade_bruta_sem_ir if not self.cupom_taxa_sem_ir else rentabilidade_bruta_sem_ir
        return rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir

    def gerar_dataframe_resultados(self):
        """Gera um DataFrame com os resultados do investimento."""
        rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir = self.calcular_rentabilidade_liquida()
        dados = {
            'Tipo de Investimento': ['Pré-fixado com IR', 'Pré-fixado Sem IR'],
            'Taxa com IR (%)': [self.taxa_com_ir * 100, ''],
            'Taxa sem IR (%)': ['', self.taxa_sem_ir * 100],
            'Cupom Mensal': [self.cupom_taxa_com_ir, self.cupom_taxa_sem_ir],
            'Rentabilidade Líquida': [rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir],
            'Investimento Inicial': [self.investimento_inicial, self.investimento_inicial],
            'Vencimento': [self.vencimento_ano, self.vencimento_ano],
        }
        return pd.DataFrame(dados)

    def calcular_aliquota_ir(self):
        """Calcula a aliquota de IR."""
        meses = self.periodo_meses
        if meses <= 6:
            return 0.225
        elif meses <= 12:
            return 0.20
        elif meses <= 24:
            return 0.175
        else:
            return 0.15

    @property
    def aliquotas_ir(self):
        """Retorna a lista de aliquotas de IR."""
        return [0.225, 0.2, 0.175, 0.15]

    @property
    def periodos_ir(self):
        """Retorna a lista de períodos para cálculo do IR."""
        total_meses = self.periodo_meses
        return [min(6, total_meses), min(6, total_meses - 6),
                min(12, total_meses - 12), total_meses - 24]

    def _calcular_rentabilidade_liquida_anual(self, taxa_anual, aliquota_ir, meses):
        """Calcula a rentabilidade líquida anual com juros simples."""
        taxa_mensal = taxa_anual / 12
        rendimento_liquido_mensal = taxa_mensal * (1 - aliquota_ir)
        rentabilidade_anual = rendimento_liquido_mensal * meses
        return rentabilidade_anual

class InvestimentoPosFixado(Investimento):
    """
    Classe para representar um investimento pós-fixado.
    """

    def __init__(self, investimento_inicial, vencimento_ano, cdi_anual, taxa_com_ir,
                 taxa_sem_ir, cupom_taxa_com_ir=False, cupom_taxa_sem_ir=False):
        super().__init__(investimento_inicial, vencimento_ano)
        self.cdi_anual = cdi_anual
        self.taxa_com_ir = taxa_com_ir
        self.taxa_sem_ir = taxa_sem_ir
        self.cupom_taxa_com_ir = cupom_taxa_com_ir
        self.cupom_taxa_sem_ir = cupom_taxa_sem_ir

    def calcular_rentabilidade_bruta(self):
        if self.cupom_taxa_com_ir or self.cupom_taxa_sem_ir:
            return self._calcular_rentabilidade_cupom()
        else:
            return self._calcular_rentabilidade_composta()

    def _calcular_rentabilidade_composta(self):
        """Calcula a rentabilidade bruta com juros compostos."""
        taxa_com_ir = self.taxa_com_ir * self.cdi_anual
        rentabilidade_com_ir = self.investimento_inicial * (
                (1 + taxa_com_ir) ** self.periodo_anos) - self.investimento_inicial
        taxa_sem_ir = self.taxa_sem_ir * self.cdi_anual
        rentabilidade_sem_ir = self.investimento_inicial * (
                (1 + taxa_sem_ir) ** self.periodo_anos) - self.investimento_inicial
        return rentabilidade_com_ir, rentabilidade_sem_ir

    def _calcular_rentabilidade_cupom(self):
        """Calcula a rentabilidade bruta com cupom mensal (juros simples)."""
        taxa_com_ir = self.taxa_com_ir * self.cdi_anual
        rentabilidade_com_ir = self._calcular_rentabilidade_liquida_cupom(taxa_com_ir)
        taxa_sem_ir = self.taxa_sem_ir * self.cdi_anual
        rentabilidade_sem_ir = self._calcular_rentabilidade_liquida_cupom(taxa_sem_ir)
        return rentabilidade_com_ir, rentabilidade_sem_ir

    def _calcular_rentabilidade_liquida_cupom(self, taxa):
        """Calcula a rentabilidade líquida com cupom mensal."""
        rentabilidade_bruta = 1
        for aliquota, periodo in zip(self.aliquotas_ir, self.periodos_ir):
            rentabilidade_bruta *= (
                1 + self._calcular_rentabilidade_liquida_anual(taxa, aliquota, periodo))
        rentabilidade_bruta -= 1
        rentabilidade_liquida = self.investimento_inicial * (1 + rentabilidade_bruta)
        rentabilidade_liquida -= self.investimento_inicial
        return rentabilidade_liquida

    def calcular_rentabilidade_liquida(self):
        rentabilidade_bruta_com_ir, rentabilidade_bruta_sem_ir = self.calcular_rentabilidade_bruta()
        ir_percent = self.calcular_aliquota_ir()
        rentabilidade_liquida_com_ir = rentabilidade_bruta_com_ir * (
            1 - ir_percent) if not self.cupom_taxa_com_ir else rentabilidade_bruta_com_ir
        rentabilidade_liquida_sem_ir = rentabilidade_bruta_sem_ir if not self.cupom_taxa_sem_ir else rentabilidade_bruta_sem_ir
        return rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir

    def gerar_dataframe_resultados(self):
        """Gera um DataFrame com os resultados do investimento."""
        rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir = self.calcular_rentabilidade_liquida()
        dados = {
            'Tipo de Investimento': ['Pós-fixado com IR', 'Pós-fixado Sem IR'],
            'CDI Anual (%)': [self.cdi_anual * 100, self.cdi_anual * 100],
            'Taxa com IR (%)': [self.taxa_com_ir * 100, ''],
            'Taxa sem IR (%)': ['', self.taxa_sem_ir * 100],
            'Cupom Mensal': [self.cupom_taxa_com_ir, self.cupom_taxa_sem_ir],
            'Rentabilidade Líquida': [rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir],
            'Investimento Inicial': [self.investimento_inicial, self.investimento_inicial],
            'Vencimento': [self.vencimento_ano, self.vencimento_ano],
        }
        return pd.DataFrame(dados)

    def calcular_aliquota_ir(self):
        """Calcula a aliquota de IR."""
        meses = self.periodo_meses
        if meses <= 6:
            return 0.225
        elif meses <= 12:
            return 0.20
        elif meses <= 24:
            return 0.175
        else:
            return 0.15

    @property
    def aliquotas_ir(self):
        """Retorna a lista de aliquotas de IR."""
        return [0.225, 0.2, 0.175, 0.15]

    @property
    def periodos_ir(self):
        """Retorna a lista de períodos para cálculo do IR."""
        total_meses = self.periodo_meses
        return [min(6, total_meses), min(6, total_meses - 6),
                min(12, total_meses - 12), total_meses - 24]

    def _calcular_rentabilidade_liquida_anual(self, taxa_anual, aliquota_ir, meses):
        """Calcula a rentabilidade líquida anual com juros simples."""
        taxa_mensal = taxa_anual / 12
        rendimento_liquido_mensal = taxa_mensal * (1 - aliquota_ir)
        rentabilidade_anual = rendimento_liquido_mensal * meses
        return rentabilidade_anual

class InvestimentoInflacao(Investimento):
    """
    Classe para representar um investimento indexado à inflação.
    """

    def __init__(self, investimento_inicial, vencimento_ano, inflacao_anual, taxa_com_ir,
                 taxa_sem_ir, cupom_taxa_com_ir=False, cupom_taxa_sem_ir=False):
        super().__init__(investimento_inicial, vencimento_ano)
        self.inflacao_anual = inflacao_anual
        self.taxa_com_ir = taxa_com_ir
        self.taxa_sem_ir = taxa_sem_ir
        self.cupom_taxa_com_ir = cupom_taxa_com_ir
        self.cupom_taxa_sem_ir = cupom_taxa_sem_ir

    def calcular_rentabilidade_bruta(self):
        if self.cupom_taxa_com_ir or self.cupom_taxa_sem_ir:
            return self._calcular_rentabilidade_cupom()
        else:
            return self._calcular_rentabilidade_composta()

    def _calcular_rentabilidade_composta(self):
        """Calcula a rentabilidade bruta com juros compostos."""
        taxa_com_ir = self.taxa_com_ir + self.inflacao_anual
        rentabilidade_com_ir = self.investimento_inicial * (
                (1 + taxa_com_ir) ** self.periodo_anos) - self.investimento_inicial
        taxa_sem_ir = self.taxa_sem_ir + self.inflacao_anual
        rentabilidade_sem_ir = self.investimento_inicial * (
                (1 + taxa_sem_ir) ** self.periodo_anos) - self.investimento_inicial
        return rentabilidade_com_ir, rentabilidade_sem_ir

    def _calcular_rentabilidade_cupom(self):
        """Calcula a rentabilidade bruta com cupom mensal (juros simples)."""
        taxa_com_ir = self.taxa_com_ir + self.inflacao_anual
        rentabilidade_com_ir = self._calcular_rentabilidade_liquida_cupom(taxa_com_ir)
        taxa_sem_ir = self.taxa_sem_ir + self.inflacao_anual
        rentabilidade_sem_ir = self._calcular_rentabilidade_liquida_cupom(taxa_sem_ir)
        return rentabilidade_com_ir, rentabilidade_sem_ir

    def _calcular_rentabilidade_liquida_cupom(self, taxa):
        """Calcula a rentabilidade líquida com cupom mensal."""
        rentabilidade_bruta = 1
        for aliquota, periodo in zip(self.aliquotas_ir, self.periodos_ir):
            rentabilidade_bruta *= (
                1 + self._calcular_rentabilidade_liquida_anual(taxa, aliquota, periodo))
        rentabilidade_bruta -= 1
        rentabilidade_liquida = self.investimento_inicial * (1 + rentabilidade_bruta)
        rentabilidade_liquida -= self.investimento_inicial
        return rentabilidade_liquida

    def calcular_rentabilidade_liquida(self):
        rentabilidade_bruta_com_ir, rentabilidade_bruta_sem_ir = self.calcular_rentabilidade_bruta()
        ir_percent = self.calcular_aliquota_ir()
        rentabilidade_liquida_com_ir = rentabilidade_bruta_com_ir * (
            1 - ir_percent) if not self.cupom_taxa_com_ir else rentabilidade_bruta_com_ir
        rentabilidade_liquida_sem_ir = rentabilidade_bruta_sem_ir if not self.cupom_taxa_sem_ir else rentabilidade_bruta_sem_ir
        return rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir

    def gerar_dataframe_resultados(self):
        """Gera um DataFrame com os resultados do investimento."""
        rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir = self.calcular_rentabilidade_liquida()
        dados = {
            'Tipo de Investimento': ['Indexado à Inflação Com IR', 'Indexado à Inflação Sem IR'],
            'Inflação Anual (%)': [self.inflacao_anual * 100, self.inflacao_anual * 100],
            'Taxa com IR (%)': [self.taxa_com_ir * 100, ''],
            'Taxa sem IR (%)': ['', self.taxa_sem_ir * 100],
            'Cupom Mensal': [self.cupom_taxa_com_ir, self.cupom_taxa_sem_ir],
            'Rentabilidade Líquida': [rentabilidade_liquida_com_ir, rentabilidade_liquida_sem_ir],
            'Investimento Inicial': [self.investimento_inicial, self.investimento_inicial],
            'Vencimento': [self.vencimento_ano, self.vencimento_ano],
        }
        return pd.DataFrame(dados)

    def calcular_aliquota_ir(self):
        """Calcula a aliquota de IR."""
        meses = self.periodo_meses
        if meses <= 6:
            return 0.225
        elif meses <= 12:
            return 0.20
        elif meses <= 24:
            return 0.175
        else:
            return 0.15

    @property
    def aliquotas_ir(self):
        """Retorna a lista de aliquotas de IR."""
        return [0.225, 0.2, 0.175, 0.15]

    @property
    def periodos_ir(self):
        """Retorna a lista de períodos para cálculo do IR."""
        total_meses = self.periodo_meses
        return [min(6, total_meses), min(6, total_meses - 6),
                min(12, total_meses - 12), total_meses - 24]

    def _calcular_rentabilidade_liquida_anual(self, taxa_anual, aliquota_ir, meses):
        """Calcula a rentabilidade líquida anual com juros simples."""
        taxa_mensal = taxa_anual / 12
        rendimento_liquido_mensal = taxa_mensal * (1 - aliquota_ir)
        rentabilidade_anual = rendimento_liquido_mensal * meses
        return rentabilidade_anual

def exibir_resultados(investimento):
    """Exibe os resultados do investimento em um DataFrame."""
    df = investimento.gerar_dataframe_resultados()
    st.dataframe(df.style.format({'Rentabilidade Líquida': "R$ {:,.2f}"}))


def main():
    """Função principal do aplicativo."""
    st.sidebar.title('Comparador Renda Fixa')
    st.sidebar.markdown('---')
    st.sidebar.subheader('Dados de Entrada')
    investimento_inicial = st.sidebar.number_input('Valor Investido', value=50000)
    vencimento_ano = st.sidebar.number_input('Vencimento', value=2026)
    st.sidebar.markdown('---')

    lista_menu = ['Pré-fixado', 'Pós Fixado', 'Inflação', 'Resumo']
    escolha = st.sidebar.radio('Escolha a opção', lista_menu)

    if escolha == 'Pré-fixado':
        st.title('Pré-fixado')
        with st.form(key='Pre'):
            taxa_com_ir = st.number_input(
                'Taxa com IR (%) (CDB)', value=15.00) / 100
            cupom_taxa_com_ir = st.checkbox(
                'Com Cupom Mensal', value=False, key='Inp_pre_taxa_com_ir')
            taxa_sem_ir = st.number_input(
                'Taxa sem IR (%) (LCI/ LCA)', value=10.50) / 100
            cupom_taxa_sem_ir = st.checkbox(
                'Com Cupom Mensal?', value=False, key='Inp_pre_taxa_sem_ir')
            st.form_submit_button('Calcular')
        investimento = InvestimentoPreFixado(
            investimento_inicial, vencimento_ano, taxa_com_ir, taxa_sem_ir,
            cupom_taxa_com_ir, cupom_taxa_sem_ir)
        exibir_resultados(investimento)

    elif escolha == 'Pós Fixado':
        st.title('Pós Fixado')
        with st.form(key='Pos'):
            cdi_anual = st.number_input(
                'CDI Anual (%)', value=11.5) / 100
            taxa_com_ir = st.number_input(
                'Taxa com IR (%) (CDB)', value=125.0) / 100
            cupom_taxa_com_ir = st.checkbox(
                'Com Cupom Mensal', value=False, key='Inp_pos_taxa_com_ir')
            taxa_sem_ir = st.number_input(
                'Taxa sem IR (%) (LCI/ LCA)', value=95.0) / 100
            cupom_taxa_sem_ir = st.checkbox(
                'Com Cupom Mensal', value=False, key='Inp_pos_taxa_sem_ir')
            st.form_submit_button('Calcular')
        investimento = InvestimentoPosFixado(
            investimento_inicial, vencimento_ano, cdi_anual, taxa_com_ir,
            taxa_sem_ir, cupom_taxa_com_ir, cupom_taxa_sem_ir)
        exibir_resultados(investimento)

    elif escolha == 'Inflação':
        st.title('Inflação')
        with st.form(key='Inflacao'):
            inflacao_anual = st.number_input(
                'Inflação Anual (%)', value=4.5) / 100
            taxa_com_ir = st.number_input(
                'Taxa com IR (%) (CDB)', value=6.8) / 100
            cupom_taxa_com_ir = st.checkbox(
                'Com Cupom Mensal', value=False, key='Inp_inflacao_taxa_com_ir')
            taxa_sem_ir = st.number_input(
                'Taxa sem IR (%) (LCI/ LCA)', value=5.3) / 100
            cupom_taxa_sem_ir = st.checkbox(
                'Com Cupom Mensal', value=False, key='Inp_inflacao_taxa_sem_ir')
            st.form_submit_button('Calcular')
        investimento = InvestimentoInflacao(
            investimento_inicial, vencimento_ano, inflacao_anual, taxa_com_ir,
            taxa_sem_ir, cupom_taxa_com_ir, cupom_taxa_sem_ir)
        exibir_resultados(investimento)

    elif escolha == 'Resumo':
        st.title('Resumo')


if __name__ == "__main__":
    main()
