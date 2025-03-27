from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
def get_dynamic_html(url):
    options = Options()
    options.add_argument("--headless")  # 브라우저 창을 열지 않음 (백그라운드 실행)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Chrome WebDriver 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 웹사이트 열기
    driver.get(url)
    time.sleep(5)  # JavaScript 실행을 기다리기 위해 5초 대기

    # 페이지의 HTML 가져오기
    html = driver.page_source
    driver.quit()  # 브라우저 종료
    return html

# 크롤링할 웹사이트 URL 입력 (반드시 실제 웹사이트 주소로 변경해주세요!)
url = "https://m.sports.naver.com/kbaseball/schedule/index?category=kbo"


# HTML 가져오기
html_content = get_dynamic_html(url)

# BeautifulSoup으로 HTML 파싱 (전체 페이지)
soup = BeautifulSoup(html_content, 'html.parser')

# class 속성이 "Home_container__"로 시작하는 div 찾기
home_container_div = soup.find('div', class_=re.compile(r'^Home_container__'))

if home_container_div:
    # 찾은 Home_container__ div의 내용만 파싱
    home_container_soup = BeautifulSoup(str(home_container_div), 'html.parser')

    # class 속성에 "ScheduleLeagueType_type_today"가 포함된 div 찾기
    today_schedule_div = home_container_soup.find('div', class_=re.compile(r'ScheduleLeagueType_type_today'))

    if today_schedule_div:
        # 찾은 ScheduleLeagueType_type_today div의 HTML 내용 (파이썬에서 사용 가능)
        today_schedule_html = str(today_schedule_div)

        soup = BeautifulSoup(html_content, 'html.parser')

        match_list_group = soup.find('div', class_=re.compile(r'ScheduleLeagueType_match_list_group__\w+ ScheduleLeagueType_type_today__\w+'))

        if match_list_group:
            match_items = match_list_group.find_all('li', class_=re.compile(r'MatchBox_match_item__\w+'))
            results = []

            for item in match_items:
                home_team = ""
                home_score = ""
                away_team = ""
                away_score = ""
                status = ""
                time_info = ""
                stadium = ""
                broadcaster = ""

                status_element = item.find('em', class_=re.compile(r'MatchBox_status__\w+'))
                status = status_element.text.strip() if status_element else ""

                time_element = item.find('div', class_=re.compile(r'MatchBox_time__\w+'))
                time_info = time_element.text.replace("경기 시간", "").strip() if time_element else ""

                stadium_element = item.find('div', class_=re.compile(r'MatchBox_stadium__\w+'))
                stadium = stadium_element.text.replace("경기장", "").strip() if stadium_element else ""

                broadcaster_element = item.find('div', class_=re.compile(r'MatchBox_add_info__\w+'))
                broadcaster = broadcaster_element.text.strip() if broadcaster_element else ""

                link_area = item.find('div', class_=re.compile(r'MatchBoxLinkArea_link_match_wrap__\w+'))
                if link_area:
                    link_elements = link_area.find_all('a', class_=re.compile(r'MatchBoxLinkArea_link_match__\w+'))


                teams_info = item.find_all('div', class_=re.compile(r'MatchBoxHeadToHeadArea_team_item__\w+'))
                scores = item.find_all('strong', class_=re.compile(r'MatchBoxHeadToHeadArea_score__\w+'))
                team_names = item.find_all('strong', class_=re.compile(r'MatchBoxHeadToHeadArea_team__\w+'))
                home_mark = item.find_all('div', class_=re.compile(r'MatchBoxHeadToHeadArea_home_mark__\w+'))

                if len(team_names) == 2 and len(scores) == 2:
                    away_team = team_names[0].text.strip()
                    away_score = scores[0].text.strip()
                    home_team = team_names[1].text.strip()
                    home_score = scores[1].text.strip()
                    if home_mark and home_mark[0].find_parent('div', class_=re.compile(r'MatchBoxHeadToHeadArea_team_name__\w+')).find('strong', class_=re.compile(r'MatchBoxHeadToHeadArea_team__\w+')).text.strip() != home_team:
                        # 순서가 홈팀, 원정팀이 아닌 경우 보정
                        away_team, home_team = home_team, away_team
                        away_score, home_score = home_score, away_score


                results.append({
                    "홈팀": home_team,
                    "홈팀 점수": home_score,
                    "원정팀": away_team,
                    "원정팀 점수": away_score,
                    "상태": status,
                    "시간": time_info,
                    "장소": stadium,
                    "중계": broadcaster,
                })

            print("| 홈팀 | 홈팀 점수 | 원정팀 | 원정팀 점수 | 상태 | 시간 | 장소 | 중계 | 기타 정보 |")
            print("|---|---|---|---|---|---|---|---|---|")
            for result in results:
                print(f"| {result['홈팀']} | {result['홈팀 점수']} | {result['원정팀']} | {result['원정팀 점수']} | {result['상태']} | {result['시간']} | {result['장소']} | {result['중계']} ")

        else:
            print("오늘 경기 정보를 찾을 수 없습니다.")

        # 필요하다면 이 내용을 파일에 저장할 수도 있습니다.
        # with open("today_schedule.html", "w", encoding="utf-8") as file:
        #     file.write(today_schedule_html)
        # print("✅ ScheduleLeagueType_type_today div 내용이 'today_schedule.html' 파일에 저장되었습니다.")

    else:
        print("⚠️ 'ScheduleLeagueType_type_today' 클래스를 포함하는 div를 찾을 수 없습니다.")

else:
    print("⚠️ 'Home_container__' 클래스를 가진 div를 찾을 수 없습니다.")

def crawl_match_info(url):
    try:
        response = requests.get(url)
       
        response.raise_for_status()  # 요청 실패 시 에러 발생

        soup = BeautifulSoup(response.text, 'html.parser')

        # 'today' 클래스를 가진 ScheduleLeagueType_match_list_group div 찾기
        today_matches_group = soup.find('div', class_=lambda x: x and 'Home_group' in x)

        print(today_matches_group, "crwa")
        results = []  # 결과를 저장할 리스트 초기화
        
        if today_matches_group:
            match_items = today_matches_group.find_all('li', class_='MatchBox_match_item_3_D0Q', limit=5)
            
            for item in match_items:
                team_area = item.find('div', class_='MatchBox_match_area_39dEr')
                if team_area:
                    teams = team_area.find_all('div', class_='MatchBoxHeadToHeadArea_team_name_3GuB0')
                    status_element = team_area.find_previous_sibling('em', class_='MatchBox_status_2pbzi')
                    
                    team_names = []  # 각 경기별 팀 이름을 저장할 리스트 초기화
                    
                    for team in teams:
                        strong_tag = team.find('strong', class_='MatchBoxHeadToHeadArea_team_40JQL')
                        if strong_tag:
                            team_names.append(strong_tag.text.strip())
                    
                    status = status_element.text.strip() if status_element else "정보 없음"
                    
                    if len(team_names) == 2:
                        results.append({
                            'home_team': team_names[1],  # 이미지상 LG가 홈팀
                            'away_team': team_names[0],  # 이미지상 한화가 원정팀
                            'status': status
                        })
            return results
        else:
            return "오늘 경기 정보가 없습니다."

    except requests.exceptions.RequestException as e:
        return f"요청 에러: {e}"
    except Exception as e:
        return f"파싱 에러: {e}"

# 크롤링할 웹페이지 URL을 여기에 입력하세요
url = "https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date=2025-03-26"


""" if isinstance(match_results, list):
    for result in match_results:
        print(f"홈팀: {result['home_team']}, 원정팀: {result['away_team']}, 상태: {result['status']}")
elif isinstance(match_results, str):
    print(match_results)
 """