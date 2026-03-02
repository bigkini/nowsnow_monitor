import cloudscraper
import json
import re

def fetch_newsnow_popular(site_name, url):
    print(f"🔍 {site_name} 정밀 스캐닝...")
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    try:
        response = scraper.get(url)
        html = response.text

        # 1. 더 강력해진 정규표현식 마커 탐색 ㅡ,.ㅡ
        # 줄바꿈 무시(re.S), 세미콜론 유무 상관없이 자바스크립트 변수 값만 낚아챔
        json_pattern = re.compile(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*(?:;|</script>)', re.DOTALL)
        match = json_pattern.search(html)

        # 만약 위 패턴으로 안 잡히면 아주 단순하게 'window.__INITIAL_STATE__=' 뒤부터 첫 '};'까지 찾음
        if not match:
            start_idx = html.find("window.__INITIAL_STATE__=")
            if start_idx != -1:
                # 시작 지점 보정
                json_start = html.find("{", start_idx)
                # 가장 가까운 script 닫는 태그나 세미콜론 찾기
                json_end = html.find("</script>", json_start)
                raw_json = html[json_start:json_end].strip()
                if raw_json.endswith(';'): raw_json = raw_json[:-1]
                data = json.loads(raw_json)
            else:
                print(f"❌ {site_name}: 마커를 도저히 찾을 수 없음.")
                return
        else:
            data = json.loads(match.group(1))

        # 2. 데이터 추출 (경로 다변화 대응)
        # US/UK 소스마다 page 계층이 있을 수도, 없을 수도 있음
        articles = []
        # 우선순위 1: page.news.mostRead
        if 'page' in data and 'news' in data['page']:
            articles = data['page']['news'].get('mostRead', [])
        # 우선순위 2: news.mostRead
        if not articles and 'news' in data:
            articles = data['news'].get('mostRead', [])

        # 3. 출력
        if articles:
            print(f"\n🏆 [{site_name}] 인기 TOP 10")
            for i, art in enumerate(articles[:10], 1):
                title = art.get('title', 'Untitled')
                domain = "https://www.newsnow.co.uk" if "co.uk" in url else "https://www.newsnow.com"
                link = art.get('url', '')
                full_url = link if link.startswith('http') else domain + link
                print(f"{i}위. {title}\n   🔗 {full_url}")
        else:
            print(f"⚠️ {site_name}: 데이터 경로는 찾았으나 기사가 비어있음.")

    except Exception as e:
        print(f"❌ {site_name} 에러: {str(e)}")

# 실행 (이전과 동일)
if __name__ == "__main__":
    targets = [
        {"name": "NewsNow US", "url": "https://www.newsnow.com/us/Sports?type=ts"},
        {"name": "NewsNow UK", "url": "https://www.newsnow.co.uk/h/Sport?type=ts"}
    ]
    for target in targets:
        fetch_newsnow_popular(target['name'], target['url'])
