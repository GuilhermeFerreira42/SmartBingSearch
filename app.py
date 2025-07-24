# app.py
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random

app = Flask(__name__)

# Constante para o número máximo de páginas a serem pesquisadas como salvaguarda
MAX_PAGES_SAFEGUARD = 50

def search_bing_page(query, page_number=0):
    """
    Realiza uma busca em uma ÚNICA página do Bing e retorna os links brutos.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    start = page_number * 10 + 1
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&first={start}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if "CAPTCHA" in response.text or "There was a problem performing your search" in response.text:
            print(f"CAPTCHA ou problema detectado na página {page_number + 1}. Parando a busca.")
            return None # Retorna None para indicar que a busca deve parar
            
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.select(".b_algo h2 a") if a.get("href") and not a["href"].startswith("https://www.bing.com")]
        
        # Pausa para evitar bloqueio
        time.sleep(random.uniform(1.0, 2.5))
        
        return list(dict.fromkeys(links))
        
    except requests.RequestException as e:
        print(f"Erro ao acessar o Bing na página {page_number + 1}: {e}")
        return [] # Retorna lista vazia em caso de erro de requisição

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
        
        if exclude_list and any(word in link_lower for word in exclude_list):
            continue
            
        if include_list and not all(word in link_lower for word in include_list):
            continue
            
        filtered_links.append(link)
            
    return filtered_links

def filter_results_by_content(links, include_words=None, exclude_words=None):
    """
    Filtra links com base em palavras-chave de inclusão e exclusão presentes no conteúdo da página.
    """
    if not include_words and not exclude_words:
        return links

    filtered_links = []
    
    include_list = [word.strip().lower() for word in include_words.split(',') if word.strip()] if include_words else []
    exclude_list = [word.strip().lower() for word in exclude_words.split(',') if word.strip()] if exclude_words else []
    
    for link in links:
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            content = response.text.lower()
            
            if exclude_list and any(word in content for word in exclude_list):
                continue
                
            if include_list and not all(word in content for word in include_list):
                continue
            
            filtered_links.append(link)
                
            time.sleep(random.uniform(1, 2))
            
        except requests.RequestException as e:
            print(f"Não foi possível acessar ou ler o link {link}: {e}")
            continue
             
    return filtered_links

def filter_links_directly(links, direct_include_links=None, direct_exclude_links=None):
    """
    Filtra links com base em uma lista direta de URLs a serem incluídas ou excluídas.
    """
    if not direct_include_links and not direct_exclude_links:
        return links

    filtered_links = []

    include_list = [line.strip().lower() for line in direct_include_links.split('\n') if line.strip()] if direct_include_links else []
    exclude_list = [line.strip().lower() for line in direct_exclude_links.split('\n') if line.strip()] if direct_exclude_links else []

    for link in links:
        link_lower = link.lower()
        
        if exclude_list and any(exclude_item in link_lower for exclude_item in exclude_list):
            continue

        if include_list and not any(include_item in link_lower for include_item in include_list):
            continue
            
        filtered_links.append(link)
            
    return filtered_links

@app.route('/', methods=['GET', 'POST'])
def index():
    context = {
        'query': '',
        'include_words': '',
        'exclude_words': '',
        'link_include_words': '',
        'link_exclude_words': '',
        'direct_include_links': '',
        'direct_exclude_links': '',
        'num_results': 10,
        'content_filters_expanded': True, # Inicia aberto por padrão
        'url_filters_expanded': False,
        'url_lists_expanded': False
    }

    if request.method == 'POST':
        query = request.form.get('searchInput', '').strip()
        include_words = request.form.get('includeWords', '').strip()
        exclude_words = request.form.get('excludeWords', '').strip()
        link_include_words = request.form.get('linkIncludeWords', '').strip()
        link_exclude_words = request.form.get('linkExcludeWords', '').strip()
        direct_include_links = request.form.get('directIncludeLinks', '').strip()
        direct_exclude_links = request.form.get('directExcludeLinks', '').strip()
        num_results_str = request.form.get('numResults', '10')
        
        # Manter o estado dos acordeões
        content_filters_expanded = request.form.get('content_filters_expanded') == 'true'
        url_filters_expanded = request.form.get('url_filters_expanded') == 'true'
        url_lists_expanded = request.form.get('url_lists_expanded') == 'true'

        context.update({
            'query': query,
            'include_words': include_words,
            'exclude_words': exclude_words,
            'link_include_words': link_include_words,
            'link_exclude_words': link_exclude_words,
            'direct_include_links': direct_include_links,
            'direct_exclude_links': direct_exclude_links,
            'content_filters_expanded': content_filters_expanded,
            'url_filters_expanded': url_filters_expanded,
            'url_lists_expanded': url_lists_expanded
        })

        if not query:
            context['error'] = "Por favor, digite um termo para pesquisar."
            return render_template('index.html', **context)

        try:
            num_results_desired = int(num_results_str)
            if not (1 <= num_results_desired <= 50):
                num_results_desired = 10
        except (ValueError, TypeError):
            num_results_desired = 10
        
        context['num_results'] = num_results_desired

        final_links = []
        processed_links = set()
        page = 0

        # Loop para buscar até atingir o número desejado de resultados ou o limite de segurança
        while len(final_links) < num_results_desired and page < MAX_PAGES_SAFEGUARD:
            print(f"Buscando na página {page + 1}...")
            links_from_page = search_bing_page(query, page_number=page)

            if links_from_page is None: # Ocorreu um CAPTCHA ou erro
                break

            new_links = [link for link in links_from_page if link not in processed_links]
            processed_links.update(new_links)
            
            # Etapa 1: Filtros rápidos (baseados em URL)
            links = filter_links_directly(new_links, direct_include_links, direct_exclude_links)
            links = filter_links_by_url(links, link_include_words, link_exclude_words)

            # Etapa 2: Filtro lento (baseado em conteúdo da página)
            if links and (include_words or exclude_words):
                filtered_content_links = filter_results_by_content(links, include_words, exclude_words)
            else:
                filtered_content_links = links

            final_links.extend(filtered_content_links)
            page += 1

        # Garante que não haja duplicatas e limita ao número desejado
        unique_final_links = list(dict.fromkeys(final_links))[:num_results_desired]
        final_results = [{'title': link, 'link': link} for link in unique_final_links]

        context['results'] = final_results
        return render_template('index.html', **context)

    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(debug=True)