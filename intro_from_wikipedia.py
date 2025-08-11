import json
import time
import uuid
import yaml
import signal
import sys
import requests
import random
import re
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from colorama import init, Fore, Back, Style

init(autoreset=True)

stop_flag = False

def signal_handler(sig, frame):
    global stop_flag
    print(f"\n{Fore.YELLOW}[INFO] Ctrl+C received. Stopping gracefully...{Style.RESET_ALL}")
    stop_flag = True

signal.signal(signal.SIGINT, signal_handler)

def load_keywords(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        keyword_data = yaml.safe_load(f)
    return keyword_data.get("KEYWORDS", [])

def load_template():
    template_path = Path(__file__).parent / "full_jsonl_template.jsonl"
    with open(template_path, "r", encoding="utf-8") as f:
        return json.loads(f.readline().strip())

def search_wikipedia(keyword, limit=10):
    """Search Wikipedia articles by keyword and get full intro section"""
    # First, search for articles matching the keyword
    search_api_url = "https://en.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": keyword,
        "srlimit": limit,
        "srprop": "title|snippet"
    }
    
    try:
        search_response = requests.get(search_api_url, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        if 'query' not in search_data or 'search' not in search_data['query']:
            return []
        
        articles = []
        for result in search_data['query']['search']:
            title = result['title']
            
            # Get the full article content
            content_params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts",
                "exintro": True,  # Only intro section (before first heading)
                "explaintext": True,  # Plain text, no HTML
                "exsectionformat": "plain"
            }
            
            content_response = requests.get(search_api_url, params=content_params)
            if content_response.status_code == 200:
                content_data = content_response.json()
                
                if 'query' in content_data and 'pages' in content_data['query']:
                    pages = content_data['query']['pages']
                    for page_id, page_data in pages.items():
                        if 'extract' in page_data and page_data['extract']:
                            articles.append({
                                'title': title,
                                'extract': page_data['extract']
                            })
                            break
            
            # Small delay to be respectful to Wikipedia API
            time.sleep(0.1)
        
        return articles
        
    except Exception as e:
        print(f"{Fore.RED}Error searching Wikipedia for '{keyword}': {e}{Style.RESET_ALL}")
        return []

def clean_wikipedia_extract(extract):
    """Clean Wikipedia extract by removing references and cleaning text"""
    if not extract:
        return ""
    
    # Remove reference markers like [1], [2], [citation needed], etc.
    extract = re.sub(r'\[\d+\]', '', extract)
    extract = re.sub(r'\[citation needed\]', '', extract)
    extract = re.sub(r'\[clarification needed\]', '', extract)
    extract = re.sub(r'\[when\?\]', '', extract)
    extract = re.sub(r'\[where\?\]', '', extract)
    extract = re.sub(r'\[who\?\]', '', extract)
    extract = re.sub(r'\[why\?\]', '', extract)
    extract = re.sub(r'\[how\?\]', '', extract)
    
    # Remove any remaining brackets with content
    extract = re.sub(r'\[.*?\]', '', extract)
    
    # Clean up extra whitespace
    extract = re.sub(r'\s+', ' ', extract)
    extract = extract.strip()
    
    # Remove common Wikipedia intro patterns that don't add value
    extract = re.sub(r'^This article is about.*?\. For.*?, see.*?\.', '', extract)
    extract = re.sub(r'^For other uses, see.*?\.', '', extract)
    extract = re.sub(r'^\S+ may refer to:', '', extract)
    
    # Clean up any remaining extra whitespace
    extract = extract.strip()
    
    return extract

def process_keyword(keyword, template, output_path):
    """Process a keyword by searching Wikipedia and extracting a clean intro"""
    articles = search_wikipedia(keyword)
    if not articles:
        return False

    # Select a random article from results
    selected_article = random.choice(articles)

    # Clean the extract
    clean_intro = clean_wikipedia_extract(selected_article['extract'])

    # Skip if the cleaned intro is too short or empty
    if len(clean_intro) < 70:
        return False

    # Create record: topic = YAML entry, keyword = Wikipedia article title, description = cleaned extract
    record = template.copy()
    record.update({
        "topic": keyword,  # YAML entry
        "keyword": selected_article['title'],  # Wikipedia article title
        "description": clean_intro
    })

    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return True

def main():
    input_path = Path(__file__).parent / "download_arxiv.yaml"  # Reuse same keywords file
    output_path = Path(__file__).parent / "intro_from_wikipedia.jsonl"
    
    keywords = load_keywords(input_path)
    template = load_template()
    
    print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}WIKIPEDIA INTRO EXTRACTION WORKFLOW{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Keywords: {Fore.BLUE}{len(keywords)}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Output: {Fore.CYAN}{output_path}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
    
    processed = 0
    errors = 0
    
    try:
        while not stop_flag:
            # Pick random keyword instead of cycling through all
            keyword = random.choice(keywords)
            
            print(f"{Fore.WHITE}Processing: {Fore.BLUE}{keyword}{Style.RESET_ALL}")
            
            success = process_keyword(keyword, template, output_path)
            if success:
                processed += 1
                print(f"{Fore.GREEN}Success: {processed} | {Fore.RED}Errors: {errors}{Style.RESET_ALL}")
            else:
                errors += 1
                print(f"{Fore.GREEN}Success: {processed} | {Fore.RED}Errors: {errors}{Style.RESET_ALL}")
            
            # Respectful delay for Wikipedia API
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO] KeyboardInterrupt detected. Stopping...{Style.RESET_ALL}")
    
    print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}WIKIPEDIA EXTRACTION STOPPED{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Total Processed: {Fore.BLUE}{processed}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Errors: {Fore.RED}{errors}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Success Rate: {Fore.GREEN}{processed/(processed+errors)*100:.1f}%{Style.RESET_ALL}" if (processed + errors) > 0 else "")
    print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()