import os
import json
import time
import re
import google.generativeai as genai
from datetime import datetime

# Gemini API 설정
GEMINI_API_KEY = os.getenv('gemini')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

# 챕터 정보
CHAPTERS_INFO = [
    ("출력", 100),
    ("변수와 입력", 100),
    ("연산자", 100),
    ("문자열1", 100),
    ("리스트 1", 100),
    ("선택제어문", 100),
    ("디버깅", 100),
    ("반복제어문 1", 100),
    ("반복제어문 2", 100),
    ("반복제어문 3", 100),
    ("문자열 2", 100),
    ("리스트 2", 100),
    ("리스트 3", 100),
    ("기타 자료형", 100),
    ("함수 1", 100),
    ("함수 2", 100),
    ("함수 3 - 재귀함수", 100),
    ("클래스", 100),
    ("파일입출력", 100)
]

PROBLEMS_DIR = "problems"

# API 호출 제한 설정 (무료 티어: 분당 5개)
MIN_REQUEST_INTERVAL = 15  # 최소 15초 간격 (분당 4개 이하로 제한)
MAX_RETRIES = 3  # 최대 재시도 횟수

def parse_retry_delay(error_message):
    """에러 메시지에서 재시도 대기 시간 추출"""
    # "Please retry in 29.538851907s" 형식에서 숫자 추출
    match = re.search(r'retry in ([\d.]+)s', error_message, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return MIN_REQUEST_INTERVAL  # 기본값

def get_difficulty_level(problem_id, total_problems):
    """문제 번호에 따라 난이도 결정"""
    if problem_id <= total_problems * 0.3:
        return "기초"
    elif problem_id <= total_problems * 0.7:
        return "중급"
    else:
        return "고급"

def generate_problem_with_gemini(chapter_name, problem_id, existing_problems, retry_count=0):
    """Gemini API를 사용하여 문제를 생성"""
    
    # 단원별 난이도 가이드라인
    difficulty_guides = {
        "출력": {
            "기초": "print() 함수 사용, 간단한 문자열 출력",
            "중급": "여러 값 출력, sep/end 파라미터 사용, 포맷팅",
            "고급": "복잡한 포맷팅, 정렬, 서식 문자 활용"
        },
        "변수와 입력": {
            "기초": "변수 선언, 기본 자료형, input() 사용",
            "중급": "여러 입력 받기, 타입 변환, 연산과 함께 사용",
            "고급": "입력 파싱, 공백/줄바꿈 처리, 복잡한 변환"
        },
        "연산자": {
            "기초": "사칙연산, 기본 연산자",
            "중급": "복합 연산자, 비교 연산, 논리 연산",
            "고급": "복잡한 수식, 우선순위, 실수 연산 정밀도"
        },
        "문자열1": {
            "기초": "문자열 생성, 인덱싱, 기본 슬라이싱",
            "중급": "문자열 메서드, 포맷팅(format, f-string), 연결",
            "고급": "서식 문자 활용, 복잡한 포맷팅, 입력 파싱과 출력 포맷팅"
        },
        "문자열 2": {
            "기초": "문자열 메서드 기본 사용",
            "중급": "문자열 검색, 치환, 분할",
            "고급": "정규표현식 개념, 복잡한 문자열 처리"
        },
        "리스트 1": {
            "기초": "리스트 생성, 인덱싱, 기본 조작",
            "중급": "리스트 메서드, 슬라이싱, 반복문과 함께",
            "고급": "리스트 컴프리헨션, 중첩 리스트, 복잡한 조작"
        },
        "선택제어문": {
            "기초": "if-else 기본, 단순 조건",
            "중급": "elif 사용, 중첩 if, 복합 조건",
            "고급": "복잡한 논리, 다중 조건, 실용적 문제"
        },
        "반복제어문 1": {
            "기초": "for 기본, range() 사용",
            "중급": "중첩 반복, 조건과 함께",
            "고급": "복잡한 패턴, 알고리즘 기초"
        },
        "반복제어문 2": {
            "기초": "while 기본, 조건 반복",
            "중급": "break/continue, 중첩 while",
            "고급": "복잡한 반복 제어, 실용적 문제"
        },
        "함수 1": {
            "기초": "함수 정의, 기본 매개변수",
            "중급": "반환값, 여러 매개변수",
            "고급": "기본값 매개변수, 가변 인자"
        }
    }
    
    total_problems = 100  # 각 단원당 100문제
    difficulty = get_difficulty_level(problem_id, total_problems)
    guide = difficulty_guides.get(chapter_name, {}).get(difficulty, "해당 단원의 적절한 난이도 문제")
    
    # 단원별 예시 문제
    example_problems = {
        "문자열1": {
            "중급": '''예시 문제:
이름과 키, 몸무게를 입력 받아 서식 문자를 사용하여 다음과 같이 출력하는 프로그램을 작성하라.

입력: "창호 170 68.47"
출력: "창호의 키는 170cm이며, 몸무게는 68.5kg입니다."

이 문제는:
- input().split()으로 여러 값 입력받기
- 서식 문자(format, f-string) 사용
- 실수 포맷팅 (68.47 -> 68.5) 필요''',
            "고급": "서식 문자를 활용한 복잡한 출력 포맷팅, 입력 파싱, 타입 변환, 실수 포맷팅 등을 포함한 실용적 문제"
        },
        "변수와 입력": {
            "중급": "여러 값을 한 줄에 입력받아 변수에 저장하고 처리하는 문제",
            "고급": "복잡한 입력 형식 파싱, 타입 변환, 검증이 필요한 문제"
        }
    }
    
    example = ""
    if chapter_name in example_problems and difficulty in example_problems[chapter_name]:
        example = f"\n\n참고 예시:\n{example_problems[chapter_name][difficulty]}"
    
    prompt = f"""
파이썬 프로그래밍 문제를 생성해주세요. JUNGOL, 백준 온라인 저지 등의 실제 코딩 테스트 문제 수준을 참고하세요.

단원: {chapter_name}
문제 번호: {problem_id}
난이도: {difficulty}
난이도 가이드: {guide}
{example}

요구사항:
1. {difficulty} 수준의 파이썬 문제를 만들어주세요
2. 문제 설명은 명확하고 이해하기 쉽게 작성해주세요
3. 입력이 필요한 경우 입력 예시를 제공해주세요 (공백으로 구분된 여러 값도 가능)
4. 출력 예시를 정확히 제공해주세요 (공백, 줄바꿈 포함)
5. 기본 코드 템플릿은 빈 상태로 제공해주세요 (정답 코드 없이)
6. 실용적이고 실제 코딩 테스트에서 나올 수 있는 문제를 만들어주세요

난이도별 특징:
- 기초: 기본 문법, 단순한 입출력, print()만 사용
- 중급: 여러 개념 조합, 입력 파싱(input().split()), 포맷팅(format/f-string), 타입 변환 필요
- 고급: 복잡한 로직, 실수 처리 및 포맷팅, 서식 문자 활용, 실용적 문제

응답 형식 (JSON):
{{
  "title": "문제 제목",
  "description": "문제 설명 (\\n으로 줄바꿈, 입력/출력 형식 명시)",
  "default_code": "# 여기에 코드를 작성하세요\\n",
  "test_cases": [
    {{"input": "입력값1", "output": "출력값1"}},
    {{"input": "입력값2", "output": "출력값2"}},
    {{"input": "입력값3", "output": "출력값3"}}
  ]
}}

중요:
- test_cases는 최소 3개 이상 제공해주세요 (다양한 케이스)
- 입력이 없는 문제는 input을 빈 문자열("")로 해주세요
- 여러 값을 입력받는 경우 공백으로 구분 (예: "이름 170 68.5")
- 출력은 정확한 문자열로 제공해주세요 (공백, 줄바꿈 정확히 일치해야 함)
- 서식 문자를 사용하는 문제의 경우 format() 또는 f-string 사용을 요구할 수 있습니다
- 실수 포맷팅이 필요한 경우 (예: 68.47 -> 68.5) 명확히 설명해주세요
- 중급 이상 문제는 입력 파싱, 타입 변환, 포맷팅 등이 포함되어야 합니다
- JSON 형식만 반환하고 다른 설명은 추가하지 마세요
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # JSON 추출 (마크다운 코드 블록 제거)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        problem_data = json.loads(response_text)
        
        # 기본 구조 보장
        if "test_cases" not in problem_data:
            problem_data["test_cases"] = [{"input": "", "output": ""}]
        
        return {
            "id": problem_id,
            "title": problem_data.get("title", f"{chapter_name} 문제 {problem_id}"),
            "description": problem_data.get("description", ""),
            "default_code": problem_data.get("default_code", "# 여기에 코드를 작성하세요\n"),
            "test_cases": problem_data.get("test_cases", [])
        }
    except Exception as e:
        error_str = str(e)
        
        # 429 에러 (할당량 초과) 처리
        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
            if retry_count < MAX_RETRIES:
                retry_delay = parse_retry_delay(error_str)
                print(f"\n⚠️ 할당량 초과 (문제 {problem_id}). {retry_delay:.1f}초 후 재시도... (시도 {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(retry_delay + 1)  # 여유를 두고 1초 추가
                return generate_problem_with_gemini(chapter_name, problem_id, existing_problems, retry_count + 1)
            else:
                print(f"\n❌ 최대 재시도 횟수 초과 (문제 {problem_id}). 기본 템플릿 사용")
        else:
            print(f"\n⚠️ 에러 발생 (문제 {problem_id}): {error_str[:100]}...")
        
        # 기본 템플릿 반환
        return {
            "id": problem_id,
            "title": f"{chapter_name} 문제 {problem_id}",
            "description": f"{chapter_name} 단원의 {problem_id}번 문제입니다.",
            "default_code": "# 여기에 코드를 작성하세요\n",
            "test_cases": [{"input": "", "output": ""}]
        }

def generate_chapter_problems(chapter_name, chapter_index, total_problems, skip_existing=True):
    """특정 챕터의 모든 문제를 생성"""
    filename = f"{chapter_index+1:02d}_{chapter_name}.json"
    filepath = os.path.join(PROBLEMS_DIR, filename)
    
    # 기존 파일이 있으면 로드
    existing_problems = {}
    if skip_existing and os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                for p in existing_data.get("problems", []):
                    existing_problems[p["id"]] = p
            print(f"\n[{chapter_name}] 기존 파일 발견: {len(existing_problems)}문제 로드됨")
        except:
            existing_problems = {}
    
    print(f"[{chapter_name}] 문제 생성 시작... (총 {total_problems}문제)")
    
    problems = []
    created_count = 0
    skipped_count = 0
    
    for i in range(1, total_problems + 1):
        if i in existing_problems and skip_existing:
            problems.append(existing_problems[i])
            skipped_count += 1
            print(f"  - {i}/{total_problems} 건너뛰기 (기존 문제) [{created_count} 생성, {skipped_count} 건너뜀]", end="\r")
        else:
            print(f"  - {i}/{total_problems} 생성 중... [{created_count} 생성, {skipped_count} 건너뜀]", end="\r")
            problem = generate_problem_with_gemini(chapter_name, i, problems)
            problems.append(problem)
            created_count += 1
            
            # API 호출 제한을 고려한 딜레이 (무료 티어: 분당 5개 제한)
            # 최소 15초 간격으로 호출하여 분당 4개 이하로 제한
            if i < total_problems:  # 마지막 문제는 대기 불필요
                time.sleep(MIN_REQUEST_INTERVAL)
    
    print(f"\n  ✓ 완료: {total_problems}문제 (신규 {created_count}개, 기존 {skipped_count}개)")
    
    # JSON 파일로 저장
    data = {
        "chapter_name": chapter_name,
        "problems": problems
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 저장 완료: {filename}\n")
    return filepath

def main():
    print("=" * 60)
    print("Gemini API를 사용한 파이썬 문제 자동 생성")
    print("=" * 60)
    
    # problems 디렉토리 생성
    os.makedirs(PROBLEMS_DIR, exist_ok=True)
    
    # 각 챕터별로 문제 생성
    for idx, (chapter_name, count) in enumerate(CHAPTERS_INFO):
        try:
            generate_chapter_problems(chapter_name, idx, count)
        except Exception as e:
            print(f"에러: {chapter_name} 챕터 생성 실패 - {e}")
            continue
    
    print("=" * 60)
    print("모든 문제 생성 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()

