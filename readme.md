# 📊 Dashboard PEP - População LGBT

Este projeto é um painel interativo construído com [Streamlit](https://streamlit.io/) para visualização e análise de dados relacionados à dispensação de PEP (Profilaxia Pós-Exposição) para populações-chave, com foco na população LGBT. Os dados foram obtidos da ANS (Agência Nacional de Saúde Suplementar) e organizados em uma planilha `.xlsx`.

---

## 📌 Funcionalidades

- Filtro por UF (estado) para análise regional.
- Visualização da distribuição de dispensações por grupo populacional.
- Gráficos comparativos por tipo de exposição e outras características sociodemográficas.
- Visualização clara e customizada com Plotly.

---

## 🧩 Tecnologias Utilizadas

- Python 3.9+ (testado com Python 3.11)
- Streamlit
- Pandas
- Plotly
- openpyxl

---

## 🚀 Instalação Passo a Passo

⚙️ **Como rodar o projeto localmente**

1. **Clone o repositório**

   ```bash
    git clone https://github.com/john1pedro2/dashboard-lgbt
    cd dashboard-pep-lgbt
    ```

2. **Crie um ambiente virtual (recomendado)**
   ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    .venv\Scripts\activate     # Windows
    ```

3. **Instale as dependências**
    O arquivo `requirements.txt` está incluído no repositório com todas as dependências necessárias.
   ```bash
    pip install -r requirements.txt
    ```
    💡 As dependências principais incluem: streamlit, pandas, plotly, openpyxl.

4. **Rode a aplicação**
   ```bash
    streamlit run app.py
    ```
    Acesse em seu navegador: http://localhost:8501

    ⚠️ Se a porta 8501 estiver em uso, o Streamlit usará outra porta automaticamente. Verifique o terminal para o endereço correto.