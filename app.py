# app.py
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random

app = Flask(__name__)

def search_bing(query, num_results_desired=10):
    """
    Realiza uma busca no Bing e retorna uma lista de links, tentando alcançar
    o número de resultados desejado, limitado a 5 páginas.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    results = []
    max_pages_to_search = 5 # Limite máximo de páginas para evitar sobrecarga

    for page in range(max_pages_to_search):
        if len(results) >= num_results_desired:
            break # Já temos resultados suficientes

        start = page * 10 + 1
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&first={start}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Lança um erro para códigos de status HTTP ruins
            
            if "CAPTCHA" in response.text or "There was a problem performing your search" in response.text:
                print("CAPTCHA detectado! Parando a execução da busca.")
                break
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Seleciona links de resultados principais, excluindo links internos do Bing
            links = [a["href"] for a in soup.select(".b_algo h2 a")
                    if a.get("href") and not a["href"].startswith("https://www.bing.com")]
            
            results.extend(links)
            
            # Pausa entre as requisições para evitar bloqueio
            if page < max_pages_to_search - 1 and len(links) > 0: # Só pausa se houver mais páginas e resultados na atual
                time.sleep(random.uniform(1.5, 4.0))
            
        except requests.RequestException as e:
            print(f"Erro ao acessar o Bing na página {page+1}: {e}")
            continue
            
    # Retorna apenas o número de resultados desejado, se houver mais
    return list(dict.fromkeys(results))[:num_results_desired]

def filter_links_by_url(links, link_include_words=None, link_exclude_words=None):
    """
    Filtra links com base em palavras-chave de inclusão e exclusão presentes na URL.
    """
    if not link_include_words and not link_exclude_words:
        return links

    filtered_links = []
    
    include_list = [word.strip().lower() for word in link_include_words.split(',') if word.strip()] if link_include_words else []
    exclude_list = [word.strip().lower() for word in link_exclude_words.split(',') if word.strip()] if link_exclude_words else []

    for link in links:
        link_lower = link.lower()
        
        # Regra de Exclusão: Se qualquer palavra de exclusão for encontrada na URL, pule este link.
        if exclude_list and any(word in link_lower for word in exclude_list):
            continue
            
        # Regra de Inclusão: Se palavras de inclusão forem fornecidas, TODAS devem estar presentes na URL.
        if include_list and not all(word in link_lower for word in include_list):
            continue
            
        filtered_links.append(link)
            
    return filtered_links

def filter_results_by_content(links, include_words=None, exclude_words=None):
    """
    Filtra links com base em palavras-chave de inclusão e exclusão presentes no conteúdo da página.
    """
    # Se nenhum filtro for fornecido, retorna a lista original de links.
    if not include_words and not exclude_words:
        return links

    filtered_links = []
    
    # Prepara as listas de palavras, removendo espaços e convertendo para minúsculas.
    # Ignora strings vazias resultantes de vírgulas extras (ex: "palavra1,,palavra2").
    include_list = [word.strip().lower() for word in include_words.split(',') if word.strip()] if include_words else []
    exclude_list = [word.strip().lower() for word in exclude_words.split(',') if word.strip()] if exclude_words else []
    
    for link in links:
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            content = response.text.lower()
            
            # Regra de Exclusão: Se qualquer palavra de exclusão for encontrada, pule este link.
            if exclude_list and any(word in content for word in exclude_list):
                continue
                
            # Regra de Inclusão: Se palavras de inclusão forem fornecidas, TODAS devem estar presentes.
            # Se a lista de inclusão estiver vazia, esta verificação é ignorada.
            if include_list and not all(word in content for word in include_list):
                continue
            
            # Se o link passou por todas as regras, adicione-o à lista final.
            filtered_links.append(link)
                
            time.sleep(random.uniform(1, 2)) # Pausa entre o acesso a cada link
            
        except requests.RequestException as e:
            print(f"Não foi possível acessar ou ler o link {link}: {e}")
            continue
            
    return filtered_links

def filter_links_directly(links, direct_include_links=None, direct_exclude_links=None):
    """
    Filtra links com base em uma lista direta de URLs a serem incluídas ou excluídas.
    Permite que partes de links sejam usadas para filtragem.
    """
    if not direct_include_links and not direct_exclude_links:
        return links

    filtered_links = []

    # Processa as entradas para remover vazios e converter para minúsculas
    # Assume que cada linha é um item a ser filtrado
    include_list = [line.strip().lower() for line in direct_include_links.split('\n') if line.strip()] if direct_include_links else []
    exclude_list = [line.strip().lower() for line in direct_exclude_links.split('\n') if line.strip()] if direct_exclude_links else []

    for link in links:
        link_lower = link.lower()
        
        # Regra de Exclusão Direta: Se o link (ou parte dele) estiver na lista de exclusão, pule.
        if exclude_list and any(exclude_item in link_lower for exclude_item in exclude_list):
            continue

        # Regra de Inclusão Direta: Se houver uma lista de inclusão, o link DEVE conter pelo menos um dos itens.
        # Se a lista de inclusão estiver vazia, esta verificação é ignorada (todos são "incluídos" por padrão desta regra).
        if include_list and not any(include_item in link_lower for include_item in include_list):
            continue
            
        filtered_links.append(link)
            
    return filtered_links

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('searchInput', '').strip()
        include_words = request.form.get('includeWords', '').strip()
        exclude_words = request.form.get('excludeWords', '').strip()
        link_include_words = request.form.get('linkIncludeWords', '').strip()
        link_exclude_words = request.form.get('linkExcludeWords', '').strip()
        direct_include_links = request.form.get('directIncludeLinks', '').strip()
        direct_exclude_links = request.form.get('directExcludeLinks', '').strip()
        num_results_str = request.form.get('numResults', '10')

        if not query:
            return render_template('index.html', error="Por favor, digite um termo para pesquisar.")

        try:
            num_results = int(num_results_str)
            if not (1 <= num_results <= 50): # Limite de resultados para evitar abusos
                num_results = 10
        except (ValueError, TypeError):
            num_results = 10

        # Passo 1: Busca inicial no Bing
        links = search_bing(query, num_results)

        # Passo 2: Aplica os filtros diretos de links primeiro, se houver
        if links and (direct_include_links or direct_exclude_links):
            links = filter_links_directly(links, direct_include_links, direct_exclude_links)

        # Passo 3: Aplica os filtros de URL, se houver
        if links and (link_include_words or link_exclude_words):
            links = filter_links_by_url(links, link_include_words, link_exclude_words)

        # Passo 4: Aplica os filtros de conteúdo, se houver links restantes e filtros de conteúdo
        if links and (include_words or exclude_words):
            final_links = filter_results_by_content(links, include_words, exclude_words)
        else:
            final_links = links # Se não houver filtros de conteúdo, os links filtrados anteriormente já são os finais

        # Passo 5: Monta a lista de resultados para exibição
        final_results = [{'title': link, 'link': link} for link in final_links]

        return render_template('index.html', 
                               results=final_results, 
                               query=query, 
                               include_words=include_words,
                               exclude_words=exclude_words, 
                               link_include_words=link_include_words,
                               link_exclude_words=link_exclude_words,
                               direct_include_links=direct_include_links,
                               direct_exclude_links=direct_exclude_links,
                               num_results=num_results)

    # Requisição GET inicial: renderiza a página limpa
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)