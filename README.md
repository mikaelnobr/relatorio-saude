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

> **Analise seus dados de saúde exportados do Xiaomi MiFitness com gráficos interativos e relatórios detalhados.**

Uma aplicação web construída com Streamlit que processa os dados exportados do app Xiaomi MiFitness (Mi Fitness / Zepp Life) e gera um dashboard visual completo + relatório em Markdown para análise por IA.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Funcionalidades

- 📱 **Upload do ZIP** exportado do MiFitness com suporte a senha (criptografia AES)
- 📅 **Seleção de período** — analise o período completo ou um intervalo personalizado
- 📊 **Dashboard interativo** com gráficos Plotly:
  - 🚶 Passos diários e distância
  - 😴 Qualidade do sono (score, fases, duração)
  - ❤️ Frequência cardíaca (repouso, zonas, SpO2)
  - 🔥 Calorias e atividade intensa
  - 💪 Treinos detalhados (musculação, caminhada, etc.)
  - 📈 Tendências e padrões semanais
- 📄 **Relatório Markdown** completo para download e análise por IA (ChatGPT, Gemini, Claude)
- 🔒 **Privacidade** — seus dados são processados localmente, nada é armazenado no servidor

---

## 🚀 Como Usar

### Passo 1: Exportar seus dados da Xiaomi

1. Acesse **[account.xiaomi.com](https://account.xiaomi.com)** e faça login com sua conta Xiaomi
2. Vá em **Privacidade** (Privacy)
3. Solicite a **exportação dos seus dados** (Data Export / Exportar Dados)
4. Aguarde o e-mail da Xiaomi com:
   - 📎 **Link para download** do arquivo ZIP com seus dados
   - 🔑 **Senha** para desbloquear o arquivo ZIP
5. Baixe o arquivo ZIP do link recebido

> ⚠️ **Importante:** O processo pode levar alguns minutos até horas. A Xiaomi envia dois e-mails separados: um com o link de download e outro com a senha.

### Passo 2: Usar a aplicação

#### Opção A: Online (Hugging Face Spaces)

Acesse diretamente pelo navegador sem instalar nada:

🔗 **[Abrir no Hugging Face Spaces](#)** *(link do seu deploy)*

#### Opção B: Rodar localmente

```bash
# Clonar o repositório
git clone https://github.com/mikaelnobr/relatorio-saude.git
cd relatorio-saude

# Instalar dependências
pip install -r requirements.txt

# Executar a aplicação
streamlit run app.py
```

### Passo 3: Gerar o relatório

1. **Envie o arquivo ZIP** na barra lateral
2. **Digite a senha** recebida por e-mail
3. **Escolha o período** (completo ou personalizado)
4. **Explore o dashboard** com os gráficos interativos
5. Vá na aba **📄 Relatório** para gerar e baixar o Markdown
6. **Envie o Markdown para uma IA** (ChatGPT, Gemini, Claude) para obter análises e recomendações personalizadas!

---

## 📁 Estrutura do Projeto

```
├── app.py                      # Aplicação Streamlit principal
├── requirements.txt            # Dependências Python
├── .streamlit/
│   └── config.toml             # Tema e configurações do Streamlit
├── src/
│   ├── __init__.py
│   ├── helpers.py              # Funções utilitárias (timestamps, formatação)
│   ├── zip_handler.py          # Extração de ZIP com senha (AES)
│   ├── csv_loader.py           # Carregamento e detecção dos CSVs
│   ├── report_builder.py       # Geração do relatório Markdown
│   ├── visualizations.py       # Gráficos Plotly interativos
│   └── processors/
│       ├── __init__.py
│       ├── profile.py          # Perfil do usuário
│       ├── devices.py          # Dispositivos conectados
│       ├── aggregated.py       # Dados agregados (passos, sono, FC, etc.)
│       ├── workouts.py         # Treinos e exercícios
│       └── trends.py           # Análise de tendências
├── gerar_relatorio.py          # Script original (standalone)
└── README.md
```

---

## 🏗️ Deploy no Hugging Face Spaces

1. Crie um novo **Space** em [huggingface.co/new-space](https://huggingface.co/new-space)
2. Selecione **Streamlit** como SDK
3. Faça upload ou conecte este repositório GitHub
4. O app será buildado automaticamente usando o `requirements.txt`

---

## 📊 Dados Suportados

O app processa os seguintes CSVs exportados pelo MiFitness:

| Arquivo | Dados |
|---------|-------|
| `hlth_center_aggregated_fitness_data.csv` | Passos, sono, FC, calorias, intensidade, estresse, SpO2 |
| `hlth_center_sport_record.csv` | Treinos e exercícios detalhados |
| `hlth_center_data_source.csv` | Dispositivos conectados |
| `user_fitness_profile.csv` | Metas e perfil fitness |
| `user_member_profile.csv` | Dados pessoais (sexo, idade, peso, altura) |

---

## 🔒 Privacidade

- ✅ Todos os dados são processados **localmente** no seu navegador/servidor
- ✅ **Nenhum dado é armazenado** permanentemente
- ✅ Os arquivos temporários são apagados após o processamento
- ✅ O código é **open source** — você pode verificar exatamente o que acontece com seus dados

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma issue ou envie um pull request.

1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  Feito com ❤️ usando <a href="https://streamlit.io">Streamlit</a> e <a href="https://plotly.com">Plotly</a>
</p>
