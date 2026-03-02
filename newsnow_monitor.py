import cloudscraper
import json
import re

def fetch_newsnow_popular(site_name, url):
    print(f"🚀 {site_name} 스캐닝 시작...")
    
    # 봇 차단 우회를 위한 스크래퍼 객체 생성
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    try:
        # 1. HTML 데이터 가져오기
        response = scraper.get(url)
        if response.status_code != 200:
            print(f"❌ 접속 실패 (상태 코드: {response.status_code})")
            return

        html = response.text

        # 2. window.__INITIAL_STATE__ JSON 추출 (정규표현식 사용) ㅡ,.ㅡ
        # 소스 코드 하단에 위치한 JSON 덩어리를 찾습니다.
        json_pattern = re.compile(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});')
        match = json_pattern.search(html)

        if not match:
            # 영국판 등에서 끝에 ;가 없을 경우를 대비한 2차 탐색
            json_pattern = re.compile(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\})</script>')
            match = json_pattern.search(html)

        if match:
            raw_json = match.group(1)
            data = json.loads(raw_json)

            # 3. 데이터 구조 내에서 Most Read 기사 경로 탐색
            # NewsNow는 국가별로 page/news 혹은 news 직하단에 데이터를 둡니다.
            articles = []
            try:
                # 경로 A (보통 미국)
                articles = data.get('page', {}).get('news', {}).get('mostRead', [])
                if not articles:
                    # 경로 B (보통 영국)
                    articles = data.get('news', {}).get('mostRead', [])
            except Exception:
                pass

            # 4. 결과 출력
            if articles:
                print(f"\n🏆 [{site_name}] 실시간 Most Read Top 10")
                print("-" * 50)
                for i, art in enumerate(articles[:10], 1):
                    title = art.get('title', '제목 없음')
                    # 상대 경로 처리 (앞에 도메인 붙이기)
                    domain = "https://www.newsnow.co.uk" if "co.uk" in url else "https://www.newsnow.com"
                    link = art.get('url', '')
                    full_url = link if link.startswith('http') else domain + link
                    
                    print(f"{i}위. {title}")
                    print(f"   🔗 {full_url}\n")
            else:
                print(f"⚠️ {site_name}: 인기 뉴스를 찾을 수 없습니다. 구조가 변경되었을 가능성이 있습니다.")
        else:
            print(f"❌ {site_name}: JSON 마커(INITIAL_STATE)를 찾지 못했습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")

# --- 실행부 ---
if __name__ == "__main__":
    targets = [
        {"name": "NewsNow US Sports", "url": "https://www.newsnow.com/us/Sports?type=ts"},
        {"name": "NewsNow UK Sport", "url": "https://www.newsnow.co.uk/h/Sport?type=ts"}
    ]

    for target in targets:
        fetch_newsnow_popular(target['name'], target['url'])
