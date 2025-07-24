# Pesquisa Avançada no Bing com Filtros de Conteúdo

Este é um aplicativo web desenvolvido em Python com o microframework Flask que permite aos usuários realizar pesquisas no Bing e filtrar os resultados de uma maneira avançada. Diferente da pesquisa padrão, esta ferramenta analisa o conteúdo de cada site retornado pela busca, exibindo apenas os resultados que contêm (ou não contêm) palavras-chave especificadas pelo usuário.
## ✨ Funcionalidades

  * **Interface Web Simples**: Uma interface limpa e intuitiva para realizar buscas.
  * **Busca no Bing**: Utiliza a pesquisa do Bing como base para encontrar resultados relevantes.
  * **Pesquisa por Número de Resultados**: Em vez de pesquisar por número de páginas, o sistema busca até encontrar o número de links desejado (limitado a 50 resultados e 5 páginas do Bing).
  * **Filtro de Conteúdo (Inclusão)**: Exibe apenas os sites que **obrigatoriamente** contenham um conjunto de palavras-chave definidas pelo usuário no *conteúdo da página*.
  * **Filtro de Conteúdo (Exclusão)**: Remove da lista de resultados os sites que contenham palavras-chave indesejadas no *conteúdo da página*.
  * **Filtro de URL (Inclusão)**: Exibe apenas os links cujas URLs **obrigatoriamente** contenham um conjunto de palavras-chave definidas pelo usuário.
  * **Filtro de URL (Exclusão)**: Remove da lista de resultados os links cujas URLs contenham palavras-chave indesejadas.
  * **Lista de Links (Inclusão)**: Permite ao usuário inserir uma lista de URLs (uma por linha) ou partes de URLs que devem ser **obrigatoriamente** incluídas nos resultados.
  * **Lista de Links (Exclusão)**: Permite ao usuário inserir uma lista de URLs (uma por linha) ou partes de URLs que devem ser excluídas dos resultados.
  * **Botão de Limpeza**: Permite limpar rapidamente todos os campos do formulário de pesquisa e filtro.
  * **Abertura em Nova Aba**: Os links dos resultados abrem em uma nova aba do navegador para uma melhor experiência de usuário.
  * **Animação de Carregamento Não Intrusiva**: A animação de carregamento aparece como um overlay sobre a área de resultados, mantendo o formulário de pesquisa acessível.
## 🚀 Tecnologias Utilizadas

  * **Backend**: Python
  * **Framework Web**: Flask
  * **Requisições HTTP**: Requests
  * **Web Scraping/Análise de HTML**: BeautifulSoup4 com `lxml`
  * **Frontend**: HTML5, Tailwind CSS

## 📂 Estrutura do Projeto