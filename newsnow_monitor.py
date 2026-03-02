import cloudscraper
import json
import re

def get_html(url):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    res = scraper.get(url)
    return res.text if res.status_code == 200 else None

# --- US 전용 추출 로직 ㅡ,.ㅡ ---
def extract_us_data(html):
    print("🇺🇸 US 데이터 파싱 시도...")
    # US는 INITIAL_STATE 뒤에 바로 </script>가 붙는 경향이 강함
    try:
        start_marker = 'window.__INITIAL_STATE__='
        start_idx = html.find(start_marker) + len(start_marker)
        # script 태그가 끝나기 전까지의 모든 중괄호 덩어리를 타격
        end_idx = html.find('</script>', start_idx)
        raw_json = html[start_idx:end_idx].strip()
        if raw_json.endswith(';'): raw_json = raw_json[:-1]
        
        data = json.loads(raw_json)
        return data.get('page', {}).get('news', {}).get('mostRead', [])
    except:
        return []

# --- UK 전용 추출 로직 ㅡ,.ㅡ ---
def extract_uk_data(html):
    print("🇬🇧 UK 데이터 파싱 시도...")
    # UK는 정규표현식이 더 잘 먹히는 구조임
    try:
        # 줄바꿈(re.S)을 포함하여 중괄호 끝까지 정밀 탐색
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', html, re.S)
        if match:
            data = json.loads(match.group(1))
            return data.get('news', {}).get('mostRead', [])
        return []
    except:
        return []

def main():
    targets = [
        {"name": "NewsNow US", "url": "https://www.newsnow.com/us/Sports?type=ts", "parser": extract_us_data},
        {"name": "NewsNow UK", "url": "https://www.newsnow.co.uk/h/Sport?type=ts", "parser": extract_uk_data}
    ]

    for target in targets:
        html = get_html(target['url'])
        if not html:
            print(f"❌ {target['name']}: 접속 실패")
            continue
            
        articles = target['parser'](html)
        
        if articles:
            print(f"\n🏆 [{target['name']}] 인기 TOP 10")
            print("-" * 40)
            domain = "https://www.newsnow.co.uk" if "co.uk" in target['url'] else "https://www.newsnow.com"
            for i, art in enumerate(articles[:10], 1):
                url = art.get('url', '')
                full_url = url if url.startswith('http') else domain + url
                print(f"{i}위. {art.get('title')}\n   🔗 {full_url}")
            print("\n")
        else:
            print(f"⚠️ {target['name']}: 데이터를 추출하지 못했습니다.")

if __name__ == "__main__":
    main()
