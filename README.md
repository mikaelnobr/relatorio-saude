---
title: MiFitness Health Report
emoji: 📊
colorFrom: red
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 📊 MiFitness Health Report

> **O seu painel pessoal de saúde! Analise os dados exportados do seu smartwatch Xiaomi (MiFitness) através de gráficos interativos e relatórios detalhados.**

Uma aplicação web completa construída com Streamlit que extrai, processa e visualiza os dados do app Xiaomi MiFitness (Mi Fitness / Zepp Life). Tenha uma visão detalhada do seu condicionamento físico, qualidade do sono, treinos e saúde cardiovascular.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Funcionalidades

- 📱 **Upload Seguro** — envie diretamente o arquivo ZIP exportado pelo MiFitness com suporte à senha original (descriptografia AES embutida)
- 📅 **Filtros Dinâmicos** — analise todo o seu histórico ou selecione um intervalo de datas personalizado
- 📊 **Dashboard Interativo** com gráficos Plotly abrangendo:
  - 🚶 Passos diários, atingimento de metas e distância percorrida
  - 😴 Qualidade do sono detalhada (score diário, fases leve/profundo/REM, duração)
  - ❤️ Frequência cardíaca (FC de repouso, zonas de treino, SpO2 e registros de estresse)
  - 🔥 Queima calórica e minutos de atividade intensa (PAI)
  - 💪 Resumo e histórico detalhado dos seus treinos físicos
  - 📈 Análise de padrões (ex: qual dia da semana você é mais ativo)
- 📑 **Exportação de Relatórios** — baixe um resumo completo em formato **PDF** estilizado ou **Markdown** para compartilhar com seu médico, personal trainer ou mesmo para enviar para uma IA (ChatGPT/Gemini)
- 🔒 **Privacidade Total** — o processamento acontece apenas na memória, nada é salvo permanentemente em nenhum banco de dados

---

## 🚀 Como Usar

### Passo 1: Exportar seus dados da Xiaomi

1. Acesse **[account.xiaomi.com](https://account.xiaomi.com)** e faça login com sua conta Xiaomi.
2. Vá na aba **Privacidade** (Privacy).
3. Solicite a **exportação dos seus dados** (Data Export / Exportar Dados).
4. Aguarde os e-mails da Xiaomi. Você receberá dois e-mails separados:
   - 📎 Um com o **Link para download** do arquivo ZIP
   - 🔑 Outro contendo a **Senha** numérica para desbloquear o arquivo
5. Baixe o arquivo ZIP para o seu computador ou celular.

### Passo 2: Acessar a aplicação

#### Opção A: Online (Hugging Face Spaces) - *Recomendado*

Acesse diretamente pelo navegador, de qualquer dispositivo, sem precisar instalar nada:

🔗 **[Abrir MiFitness Health Report](https://mikaelnobr-relatorio-saude.hf.space)**

#### Opção B: Rodar localmente

```bash
# Clone o repositório
git clone https://github.com/mikaelnobr/relatorio-saude.git
cd relatorio-saude

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação Streamlit
streamlit run app.py
```

### Passo 3: Gerar seu painel

1. Na barra lateral da aplicação, faça o **upload do arquivo ZIP**.
2. Digite a **senha** que você recebeu por e-mail.
3. Aguarde o processamento automático dos seus arquivos (gera o dashboard na hora).
4. Navegue pelas diferentes abas (Resumo, Passos, Sono, Treinos, etc).
5. Se desejar, acesse a aba **Relatório** e faça o download em **PDF** para manter salvo!

---

## 📁 Estrutura do Projeto

```
├── app.py                      # Aplicação principal (Dashboard Streamlit)
├── requirements.txt            # Dependências Python (pandas, plotly, streamlit, etc)
├── Dockerfile                  # Container para deploy padrão via Docker
├── .replit                     # Configurações para hospedar no ambiente Replit
├── .streamlit/
│   └── config.toml             # Configuração de tema escuro e layout
├── src/
│   ├── helpers.py              # Utilitários (formatação de datas, números)
│   ├── zip_handler.py          # Lida com a criptografia e extração do ZIP
│   ├── csv_loader.py           # Varredura autônoma dos arquivos CSVs certos
│   ├── report_builder.py       # Gerador do relatório bruto em Markdown
│   ├── pdf_generator.py        # Gerador do relatório formatado em PDF (usando fpdf2)
│   ├── visualizations.py       # Códigos dos gráficos interativos Plotly
│   └── processors/             # Módulos segmentados de processamento
│       ├── profile.py          # Perfil fisiológico do usuário
│       ├── devices.py          # Dispositivos linkados (Mi Band, Watch, etc)
│       ├── aggregated.py       # Dados macro (passos, HR diária, etc)
│       ├── workouts.py         # Histórico de treinos
│       └── trends.py           # Tendências semanais e evolução no período
└── README.md
```

---

## 🏗️ Deploy do seu próprio servidor

Se quiser ter a sua própria cópia rodando na nuvem:

**Hugging Face Spaces:**
Basta criar um novo *Space*, selecionar **Docker** como ambiente e linkar este seu repositório do GitHub. O `Dockerfile` nativo da aplicação tomará conta do resto (porta 7860).

**Replit:**
Crie um novo *Repl*, importe o link do seu GitHub e clique em "Run". O arquivo `.replit` subirá na porta 5000.

---

## 📊 Arquivos CSV Monitorados

O sistema varre os arquivos dinâmicos contidos no ZIP procurando os seguintes padrões:

| Arquivo Fonte | Dados Extraídos |
|---------|-------|
| `..._hlth_center_aggregated_fitness_data.csv` | Passos, métricas de sono, FC contínua, kcal, etc. |
| `..._hlth_center_sport_record.csv` | Treinos e atividades esportivas finalizadas. |
| `..._hlth_center_data_source.csv` | Hardwares e wearables identificados. |
| `..._user_fitness_profile.csv` | Metas estipuladas no app da Xiaomi. |
| `..._user_member_profile.csv` | Físico do usuário (sexo, idade, IMC, peso). |

---

## 🤝 Contribuindo

Ideias ou melhorias? Fique à vontade para mandar um pull request!

1. Fork o projeto
2. Crie uma branch para sua adaptação (`git checkout -b feature/minha-ideia`)
3. Commit suas mudanças (`git commit -m 'feat: minha nova feature incrível'`)
4. Faça o Push (`git push origin feature/minha-ideia`)
5. Abra e submeta um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Refira-se ao arquivo `LICENSE` no repositório.

---

<p align="center">
  Feito com ❤️ por <a href="https://github.com/mikaelnobr">mikaelnobr</a>
</p>
