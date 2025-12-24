import json
import os
import random

# 단원별 문제 생성 가이드라인
PROBLEM_TEMPLATES = {
    "출력": {
        "기초": [
            ("문자열 출력", "화면에 '{text}'를 출력하시오.", ""),
            ("숫자 출력", "숫자 {num}을 출력하시오.", ""),
            ("여러 값 출력", "{val1}, {val2}, {val3}을 각각 줄을 바꿔 출력하시오.", ""),
        ],
        "중급": [
            ("포맷팅 출력", "변수 name='{name}', age={age}일 때, 'My name is {name} and I am {age} years old.'를 출력하시오.", "name = '{name}'\nage = {age}\n# 여기에 코드를 작성하세요\n"),
            ("sep 사용", "{a}, {b}, {c}을 출력하되, 값 사이에 '{sep}'를 넣어 출력하시오. (sep 옵션 사용)", ""),
            ("end 사용", "print 함수를 여러 번 사용하여 '{text1}'와 '{text2}'를 한 줄에 출력하시오. (end 옵션 사용)", ""),
        ],
        "고급": [
            ("서식 문자", "변수 price={price}일 때, 'The price is ${price:.2f}' 형식으로 출력하시오.", "price = {price}\n# 여기에 코드를 작성하세요\n"),
            ("정렬 출력", "문자열 '{text}'를 {width}자리로 {align} 정렬하여 출력하시오.", ""),
        ]
    },
    "변수와 입력": {
        "기초": [
            ("변수 선언", "변수 {var}에 {val}을 저장하고 출력하시오.", ""),
            ("입력 받기", "키보드로 문자열을 입력받아 변수 {var}에 저장하고 출력하시오.", ""),
        ],
        "중급": [
            ("여러 값 입력", "이름과 나이를 입력받아(공백 구분), '제 이름은 {name}이고, 나이는 {age}살입니다.' 형식으로 출력하시오.", ""),
            ("타입 변환", "정수를 입력받아 그 수의 제곱을 출력하시오.", ""),
        ],
        "고급": [
            ("복잡한 입력 파싱", "이름, 키, 몸무게를 입력받아(공백 구분) 서식 문자를 사용하여 '{name}의 키는 {height}cm이며, 몸무게는 {weight:.1f}kg입니다.' 형식으로 출력하시오.", ""),
        ]
    }
}

def generate_problem_content(chapter_name, problem_id, difficulty):
    """난이도에 따라 문제 내용 생성"""
    # 간단한 문제 생성 로직
    if chapter_name == "출력":
        if difficulty == "기초":
            if problem_id <= 10:
                return {
                    "title": f"기본 출력 {problem_id}",
                    "description": f"화면에 'Problem {problem_id}'를 출력하시오.",
                    "default_code": "# 여기에 코드를 작성하세요\n",
                    "test_cases": [{"input": "", "output": f"Problem {problem_id}"}]
                }
            else:
                texts = ["Hello", "World", "Python", "Programming", "Test"]
                return {
                    "title": f"문자열 출력 {problem_id}",
                    "description": f"화면에 '{random.choice(texts)}'를 출력하시오.",
                    "default_code": "# 여기에 코드를 작성하세요\n",
                    "test_cases": [{"input": "", "output": random.choice(texts)}]
                }
        elif difficulty == "중급":
            return {
                "title": f"포맷팅 출력 {problem_id}",
                "description": f"변수 a={problem_id*10}, b={problem_id*5}일 때, 'a={problem_id*10}, b={problem_id*5}'를 format() 또는 f-string을 사용하여 출력하시오.",
                "default_code": f"a = {problem_id*10}\nb = {problem_id*5}\n# 여기에 코드를 작성하세요\n",
                "test_cases": [{"input": "", "output": f"a={problem_id*10}, b={problem_id*5}"}]
            }
        else:  # 고급
            return {
                "title": f"복잡한 포맷팅 {problem_id}",
                "description": f"변수 name='Student{problem_id}', score={problem_id*10.5:.1f}일 때, 'Student{problem_id}의 점수는 {problem_id*10.5:.1f}점입니다.'를 서식 문자를 사용하여 출력하시오.",
                "default_code": f"name = 'Student{problem_id}'\nscore = {problem_id*10.5}\n# 여기에 코드를 작성하세요\n",
                "test_cases": [{"input": "", "output": f"Student{problem_id}의 점수는 {problem_id*10.5:.1f}점입니다."}]
            }
    
    # 기본 템플릿 (다른 단원들)
    return {
        "title": f"{chapter_name} 문제 {problem_id}",
        "description": f"{chapter_name} 단원의 {problem_id}번 문제입니다. 이 문제는 Gemini API를 사용하여 생성해야 합니다.",
        "default_code": "# 여기에 코드를 작성하세요\n",
        "test_cases": [{"input": "", "output": ""}]
    }

def fill_problems_file(filepath):
    """문제 파일의 빈 템플릿을 채움"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chapter_name = data['chapter_name']
    problems = data['problems']
    
    updated_count = 0
    for problem in problems:
        # 템플릿 문제인지 확인 (description에 "Gemini API"가 포함되어 있으면)
        if "Gemini API를 사용하여 생성해야 합니다" in problem.get('description', ''):
            problem_id = problem['id']
            difficulty = "기초" if problem_id <= 30 else ("중급" if problem_id <= 70 else "고급")
            
            # 실제 문제 내용 생성
            new_content = generate_problem_content(chapter_name, problem_id, difficulty)
            problem.update(new_content)
            updated_count += 1
    
    if updated_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"{filepath}: {updated_count}개 문제 내용 생성 완료")
    else:
        print(f"{filepath}: 업데이트할 문제가 없습니다.")

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
            fill_problems_file(filepath)

if __name__ == "__main__":
    main()

