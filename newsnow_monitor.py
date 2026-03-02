import cloudscraper
import json
import re

def get_html(url):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    res = scraper.get(url)
    return res.text if res.status_code == 200 else None

def extract_balanced_json(html, start_marker):
    """중괄호 짝을 맞춰서 가장 정확한 JSON 덩어리를 추출합니다 ㅡ,.ㅡ"""
    start_idx = html.find(start_marker)
    if start_idx == -1: return None
    
    json_start_idx = html.find('{', start_idx)
    if json_start_idx == -1: return None
    
    count = 0
    for i in range(json_start_idx, len(html)):
        if html[i] == '{':
            count += 1
        elif html[i] == '}':
            count -= 1
            if count == 0:
                return html[json_start_idx : i + 1]
    return None

def parse_newsnow(name, url):
    print(f"🔍 {name} 데이터 추출 중...")
    html = get_html(url)
    if not html:
        print("❌ HTML 로드 실패")
        return

    # 1. 중괄호 짝 맞추기 로직으로 JSON 추출
    raw_json = extract_balanced_json(html, 'window.__INITIAL_STATE__=')
    
    if not raw_json:
        print("❌ INITIAL_STATE 마커를 찾지 못했습니다.")
        return

    try:
        data = json.loads(raw_json)
        
        # 2. 경로 유연화 (US/UK 통합 대응) ㅡ,.ㅡ
        # page.news.mostRead 혹은 news.mostRead 둘 다 확인
        articles = []
        if 'page' in data and 'news' in data['page']:
            articles = data['page']['news'].get('mostRead', [])
        
        if not articles and 'news' in data:
            articles = data['news'].get('mostRead', [])

        # 3. 결과 출력
        if articles:
            print(f"\n🏆 [{name}] Most Read Top 10")
            print("-" * 45)
            domain = "https://www.newsnow.co.uk" if "co.uk" in url else "https://www.newsnow.com"
            for i, art in enumerate(articles[:10], 1):
                title = art.get('title')
                link = art.get('url', '')
                full_url = link if link.startswith('http') else domain + link
                print(f"{i}위. {title}\n   🔗 {full_url}")
            print("\n")
        else:
            print("⚠️ 데이터 경로는 찾았으나 기사가 비어있습니다.")
            
    except Exception as e:
        print(f"❌ JSON 파싱 에러: {str(e)}")

if __name__ == "__main__":
    parse_newsnow("NewsNow US", "https://www.newsnow.com/us/Sports?type=ts")
    parse_newsnow("NewsNow UK", "https://www.newsnow.co.uk/h/Sport?type=ts")
