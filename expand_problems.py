import json
import os

# 단원별 난이도 가이드라인 (generate_problems_gemini.py에서 가져옴)
DIFFICULTY_GUIDES = {
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
    "디버깅": {
        "기초": "문법 오류 수정, 들여쓰기 오류",
        "중급": "변수명 오류, 논리 오류 수정",
        "고급": "타입 오류, 복잡한 버그 수정"
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
    "반복제어문 3": {
        "기초": "break/continue 기본",
        "중급": "중첩 반복문에서 break/continue",
        "고급": "복잡한 반복 제어, 알고리즘 문제"
    },
    "리스트 2": {
        "기초": "리스트 메서드 기본",
        "중급": "리스트 컴프리헨션, 정렬, 필터링",
        "고급": "복잡한 리스트 조작, 알고리즘"
    },
    "리스트 3": {
        "기초": "2차원 리스트 기본",
        "중급": "2차원 리스트 조작, 전치",
        "고급": "복잡한 2차원 리스트 처리, 행렬 연산"
    },
    "기타 자료형": {
        "기초": "튜플, 딕셔너리, 집합 기본",
        "중급": "딕셔너리 조작, 집합 연산",
        "고급": "복잡한 자료형 조합, 실용적 문제"
    },
    "함수 1": {
        "기초": "함수 정의, 기본 매개변수",
        "중급": "반환값, 여러 매개변수",
        "고급": "기본값 매개변수, 가변 인자"
    },
    "함수 2": {
        "기초": "람다 함수, map/filter",
        "중급": "가변 인자, 키워드 인자",
        "고급": "클로저, 데코레이터, 고급 함수"
    },
    "함수 3 - 재귀함수": {
        "기초": "재귀 함수 기본, 팩토리얼",
        "중급": "피보나치, 재귀 합계",
        "고급": "복잡한 재귀, 하노이 탑, 알고리즘"
    },
    "클래스": {
        "기초": "클래스 정의, 생성자, 메서드",
        "중급": "상속, 오버라이딩",
        "고급": "프로퍼티, 메서드 체이닝, 고급 클래스"
    },
    "파일입출력": {
        "기초": "파일 읽기/쓰기 기본",
        "중급": "여러 줄 처리, 파일 모드",
        "고급": "복잡한 파일 처리, 데이터 파싱"
    }
}

def get_difficulty_level(problem_id, total_problems):
    """문제 번호에 따라 난이도 결정"""
    if problem_id <= total_problems * 0.3:
        return "기초"
    elif problem_id <= total_problems * 0.7:
        return "중급"
    else:
        return "고급"

def generate_problem_template(chapter_name, problem_id, difficulty):
    """프롬프트 가이드라인에 따라 문제 템플릿 생성"""
    guide = DIFFICULTY_GUIDES.get(chapter_name, {}).get(difficulty, "해당 단원의 적절한 난이도 문제")
    
    # 기본 템플릿 (실제로는 Gemini API로 생성해야 하지만, 여기서는 구조만 제공)
    return {
        "id": problem_id,
        "title": f"{chapter_name} 문제 {problem_id} ({difficulty})",
        "description": f"{chapter_name} 단원의 {problem_id}번 문제입니다.\n\n난이도: {difficulty}\n가이드: {guide}\n\n이 문제는 Gemini API를 사용하여 생성해야 합니다.",
        "default_code": "# 여기에 코드를 작성하세요\n",
        "test_cases": [
            {"input": "", "output": ""}
        ]
    }

def expand_problems_file(filepath, target_count=100):
    """문제 파일을 target_count개까지 확장"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chapter_name = data['chapter_name']
    existing_problems = data['problems']
    existing_count = len(existing_problems)
    
    if existing_count >= target_count:
        print(f"{filepath}: 이미 {existing_count}개 문제가 있습니다. (목표: {target_count}개)")
        return
    
    # 기존 문제 ID 추출
    existing_ids = {p['id'] for p in existing_problems}
    
    # 새로운 문제 생성
    new_problems = []
    for i in range(1, target_count + 1):
        if i not in existing_ids:
            difficulty = get_difficulty_level(i, target_count)
            new_problem = generate_problem_template(chapter_name, i, difficulty)
            new_problems.append(new_problem)
    
    # 기존 문제와 새 문제 합치기
    all_problems = existing_problems + new_problems
    all_problems.sort(key=lambda x: x['id'])
    
    # 데이터 업데이트
    data['problems'] = all_problems
    
    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"{filepath}: {existing_count}개 → {len(all_problems)}개 확장 완료 (새로 추가: {len(new_problems)}개)")

def main():
    problems_dir = "problems"
    files = [
        "01_출력.json",
        "02_변수와 입력.json",
        "03_연산자.json",
        "04_문자열1.json",
        "05_리스트 1.json",
        "06_선택제어문.json",
        "07_디버깅.json",
        "08_반복제어문 1.json",
        "09_반복제어문 2.json",
        "10_반복제어문 3.json",
        "11_문자열 2.json",
        "12_리스트 2.json",
        "13_리스트 3.json",
        "14_기타 자료형.json",
        "15_함수 1.json",
        "16_함수 2.json",
        "17_함수 3 - 재귀함수.json",
        "18_클래스.json",
        "19_파일입출력.json"
    ]
    
    for filename in files:
        filepath = os.path.join(problems_dir, filename)
        if os.path.exists(filepath):
            expand_problems_file(filepath, 100)
        else:
            print(f"{filepath}: 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()

