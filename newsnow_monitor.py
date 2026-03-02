import cloudscraper
import json
import re

def get_html(url):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    # 캐시 방지를 위해 타임스탬프 추가 ㅡ,.ㅡ
    res = scraper.get(f"{url}&_={re.sub(r'[^0-9]', '', str(__import__('time').time()))}")
    return res.text if res.status_code == 200 else None

def force_clean_json(raw_str):
    """JSON 내부의 자바스크립트 특수문자를 강제로 제거/치환합니다."""
    # 1. undefined 치환
    raw_str = raw_str.replace(":undefined", ":null")
    # 2. 제어 문자 제거
    raw_str = "".join(ch for ch in raw_str if ord(ch) >= 32)
    return raw_str

def extract_balanced_json(html, start_marker):
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
    print(f"🔍 {name} 파싱 시도 중...")
    html = get_html(url)
    
    if not html or "window.__INITIAL_STATE__" not in html:
        # 만약 HTML이 비었거나 마커가 없다면 차단된 것임
        print(f"❌ {name}: HTML에 데이터가 없습니다. (Access Denied 가능성)")
        return

    raw_json = extract_balanced_json(html, 'window.__INITIAL_STATE__=')
    if not raw_json:
        print(f"❌ {name}: JSON 데이터를 잘라내지 못했습니다.")
        return

    try:
        # 강제 정제 로직 투입 ㅡ,.ㅡ
        clean_json = force_clean_json(raw_json)
        data = json.loads(clean_json)
        
        # 기사 탐색 (모든 가능 경로)
        articles = []
        paths = [
            ['page', 'news', 'mostRead'],
            ['news', 'mostRead'],
            ['page', 'news', 'topStories'] # 인기 뉴스가 없을 때 톱 뉴스로 대체
        ]
        
        for path in paths:
            temp = data
            for key in path:
                if isinstance(temp, dict):
                    temp = temp.get(key, {})
            if isinstance(temp, list) and len(temp) > 0:
                articles = temp
                break

        if articles:
            print(f"\n🏆 [{name}] 성공!")
            domain = "https://www.newsnow.co.uk" if "co.uk" in url else "https://www.newsnow.com"
            for i, art in enumerate(articles[:10], 1):
                full_url = art['url'] if art['url'].startswith('http') else domain + art['url']
                print(f"{i}위. {art.get('title')}\n   🔗 {full_url}")
        else:
            print(f"⚠️ {name}: 데이터 구조는 파싱했으나 기사 리스트가 비어있음.")
            
    except Exception as e:
        print(f"❌ {name} JSON 해석 실패: {str(e)}")

if __name__ == "__main__":
    # US부터 집중 타격
    parse_newsnow("NewsNow US", "https://www.newsnow.com/us/Sports?type=ts")
    parse_newsnow("NewsNow UK", "https://www.newsnow.co.uk/h/Sport?type=ts")
