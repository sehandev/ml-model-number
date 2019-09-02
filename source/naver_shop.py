from difflib import SequenceMatcher
import urllib.request
import json
import re

nek = re.compile("[^ 0-9A-Z가-힣]+")  # number, english, korean

검색결과수 = "10"
검색시작위치 = "1"

client_id = "mU7lxA6TYFltEmTZKWsE"
client_secret = "aq7XXTALdT"


def naver_shop(query):
    # query를 네이버 쇼핑에서 검색

    검색어 = urllib.parse.quote(query)
    url = "https://openapi.naver.com/v1/search/shop"
    url += "?query=" + 검색어
    url += "&display=" + 검색결과수
    url += "&start=" + 검색시작위치
    url += "&sort=sim"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode == 200):
            response_body = response.read()
            return response_body
        else:
            print("Error Code:" + rescode)
            return ""
    except Exception as exception:
        print("Exception : " + str(exception))
        print("error query : " + query)


def model_name_score(query):
    response_body = naver_shop(query)  # query를 네이버 쇼핑 검색

    json_result = json.loads(response_body)  # 검색결과 -> dict

    compare_list = []

    for item in json_result["items"]:
        # 상품 하나에 대해서

        title = item["title"]  # 상품명
        left = title  # 검색어 제외

        bolds = re.findall("<b>.+</b>", title)  # 검색어 찾기
        for bold in bolds:
            if bold[3:-4] != query:
                # 검색어와 다른 경우
                print("\nwarning : " + query)
                print("bold : " + bold[3:-4] + '\n')
            left = left.replace(bold, "")  # 검색어 제외

        left = nek.sub(" ", left)  # 숫자, 영어, 한글
        left = ' '.join(left.split())  # 공백 1칸으로 통일
        left = left.strip()  # 전후 공백 제거
        compare_list.append(left)

    similar_score = []
    for i in range(len(compare_list)):
        high_score = 0.0
        for j in list(range(0, i)) + list(range(i+1, len(compare_list))):
            new_score = round(SequenceMatcher(None, compare_list[i], compare_list[j]).ratio(), 2)
            if high_score < new_score < 1.0:
                high_score = new_score
        similar_score.append(high_score)
    return similar_score

if __name__ == "__main__":
    score = model_name_score("455X610mm")
    print(score)
