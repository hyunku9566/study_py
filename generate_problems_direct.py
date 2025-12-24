"""
프롬프트 가이드라인에 따라 각 단원별로 100개 문제를 생성하는 스크립트
기존 문제는 유지하고, 빈 템플릿만 있는 문제들을 실제 문제로 채움
"""
import json
import os
import random

def get_difficulty(problem_id):
    """문제 번호에 따라 난이도 결정"""
    if problem_id <= 30:
        return "기초"
    elif problem_id <= 70:
        return "중급"
    else:
        return "고급"

def generate_output_problem(problem_id, difficulty):
    """출력 단원 문제 생성"""
    if difficulty == "기초":
        patterns = [
            ("기본 문자열 출력", f"화면에 'Output {problem_id}'를 출력하시오.", ""),
            ("숫자 출력", f"숫자 {problem_id * 10}을 출력하시오.", ""),
            ("여러 줄 출력", f"다음과 같이 출력하시오:\n\nLine {problem_id}\nLine {problem_id + 1}", ""),
            ("특수문자 출력", f"화면에 '{'!' * problem_id}'를 출력하시오.", ""),
        ]
    elif difficulty == "중급":
        patterns = [
            ("포맷팅 출력", f"변수 name='Student{problem_id}', age={20 + problem_id}일 때, 'My name is Student{problem_id} and I am {20 + problem_id} years old.'를 format() 또는 f-string을 사용하여 출력하시오.", f"name = 'Student{problem_id}'\nage = {20 + problem_id}\n# 여기에 코드를 작성하세요\n"),
            ("sep 사용", f"{problem_id}, {problem_id*2}, {problem_id*3}을 출력하되, 값 사이에 ':'를 넣어 출력하시오.", ""),
            ("end 사용", f"print 함수를 여러 번 사용하여 'Part{problem_id}'와 'Part{problem_id+1}'를 한 줄에 출력하시오.", ""),
        ]
    else:  # 고급
        patterns = [
            ("서식 문자", f"변수 price={problem_id * 100.5:.2f}일 때, 'The price is ${problem_id * 100.5:.2f}' 형식으로 출력하시오.", f"price = {problem_id * 100.5}\n# 여기에 코드를 작성하세요\n"),
            ("정렬 출력", f"문자열 'Item{problem_id}'를 15자리로 오른쪽 정렬하여 출력하시오.", ""),
            ("복잡한 포맷팅", f"변수 name='User{problem_id}', score={problem_id * 10.5:.1f}, grade='A'일 때, 'User{problem_id}의 점수는 {problem_id * 10.5:.1f}점이며, 등급은 A입니다.'를 출력하시오.", f"name = 'User{problem_id}'\nscore = {problem_id * 10.5}\ngrade = 'A'\n# 여기에 코드를 작성하세요\n"),
        ]
    
    pattern = random.choice(patterns)
    title, desc, code = pattern
    
    # test_cases 생성
    if "출력하시오" in desc:
        # 출력 추출
        if "format()" in desc or "f-string" in desc:
            # 포맷팅 문제
            output = desc.split("'")[-2] if "'" in desc else desc.split('"')[-2] if '"' in desc else f"Output {problem_id}"
        else:
            output = desc.split("'")[1] if "'" in desc else desc.split('"')[1] if '"' in desc else f"Output {problem_id}"
    else:
        output = f"Output {problem_id}"
    
    return {
        "title": title,
        "description": desc,
        "default_code": code if code else "# 여기에 코드를 작성하세요\n",
        "test_cases": [{"input": "", "output": output}]
    }

def generate_variable_input_problem(problem_id, difficulty):
    """변수와 입력 단원 문제 생성"""
    if difficulty == "기초":
        return {
            "title": f"변수 선언 {problem_id}",
            "description": f"변수 num에 {problem_id * 10}을 저장하고 출력하시오.",
            "default_code": "# 여기에 코드를 작성하세요\n",
            "test_cases": [{"input": "", "output": str(problem_id * 10)}]
        }
    elif difficulty == "중급":
        return {
            "title": f"여러 값 입력 {problem_id}",
            "description": f"이름과 나이를 입력받아(공백 구분), '제 이름은 [이름]이고, 나이는 [나이]살입니다.' 형식으로 출력하시오.",
            "default_code": "# 여기에 코드를 작성하세요\n",
            "test_cases": [
                {"input": f"User{problem_id} {20 + problem_id}", "output": f"제 이름은 User{problem_id}이고, 나이는 {20 + problem_id}살입니다."},
                {"input": f"Test{problem_id} {25 + problem_id}", "output": f"제 이름은 Test{problem_id}이고, 나이는 {25 + problem_id}살입니다."}
            ]
        }
    else:  # 고급
        return {
            "title": f"복잡한 입력 파싱 {problem_id}",
            "description": f"이름, 키, 몸무게를 입력받아(공백 구분) 서식 문자를 사용하여 '[이름]의 키는 [키]cm이며, 몸무게는 [몸무게]kg입니다.' 형식으로 출력하시오. (몸무게는 소수점 첫째자리까지)",
            "default_code": "# 여기에 코드를 작성하세요\n",
            "test_cases": [
                {"input": f"Person{problem_id} {170 + problem_id} {65.5 + problem_id}", "output": f"Person{problem_id}의 키는 {170 + problem_id}cm이며, 몸무게는 {65.5 + problem_id:.1f}kg입니다."},
                {"input": f"Student{problem_id} {175 + problem_id} {70.3 + problem_id}", "output": f"Student{problem_id}의 키는 {175 + problem_id}cm이며, 몸무게는 {70.3 + problem_id:.1f}kg입니다."}
            ]
        }

def generate_operator_problem(problem_id, difficulty):
    """연산자 단원 문제 생성"""
    if difficulty == "기초":
        return {
            "title": f"기본 연산 {problem_id}",
            "description": f"{problem_id * 10}과 {problem_id * 5}의 합을 출력하시오.",
            "default_code": "# 여기에 코드를 작성하세요\n",
            "test_cases": [{"input": "", "output": str(problem_id * 15)}]
        }
    elif difficulty == "중급":
        return {
            "title": f"복합 연산 {problem_id}",
            "description": f"변수 a={problem_id}, b={problem_id*2}일 때, a += b 연산을 수행하고 a를 출력하시오.",
            "default_code": f"a = {problem_id}\nb = {problem_id*2}\n# 여기에 코드를 작성하세요\n",
            "test_cases": [{"input": "", "output": str(problem_id * 3)}]
        }
    else:
        return {
            "title": f"복잡한 수식 {problem_id}",
            "description": f"변수 a={problem_id}, b={problem_id*2}, c={problem_id*3}일 때, (a + b) * c - a를 계산하여 출력하시오.",
            "default_code": f"a = {problem_id}\nb = {problem_id*2}\nc = {problem_id*3}\n# 여기에 코드를 작성하세요\n",
            "test_cases": [{"input": "", "output": str((problem_id + problem_id*2) * problem_id*3 - problem_id)}]
        }

def generate_string1_problem(problem_id, difficulty):
    """문자열1 단원 문제 생성"""
    if difficulty == "기초":
        return {
            "title": f"문자열 기본 {problem_id}",
            "description": f"문자열 'String{problem_id}'를 출력하시오.",
            "default_code": "# 여기에 코드를 작성하세요\n",
            "test_cases": [{"input": "", "output": f"String{problem_id}"}]
        }
    elif difficulty == "중급":
        return {
            "title": f"문자열 포맷팅 {problem_id}",
            "description": f"변수 name='User{problem_id}', age={20 + problem_id}일 때, f-string을 사용하여 'My name is User{problem_id} and I am {20 + problem_id} years old.'를 출력하시오.",
            "default_code": f"name = 'User{problem_id}'\nage = {20 + problem_id}\n# 여기에 코드를 작성하세요\n",
            "test_cases": [{"input": "", "output": f"My name is User{problem_id} and I am {20 + problem_id} years old."}]
        }
    else:
        return {
            "title": f"서식 문자 활용 {problem_id}",
            "description": f"이름과 키, 몸무게를 입력받아(공백 구분) 서식 문자를 사용하여 '[이름]의 키는 [키]cm이며, 몸무게는 [몸무게]kg입니다.' 형식으로 출력하시오. (몸무게는 소수점 첫째자리까지)",
            "default_code": "# 여기에 코드를 작성하세요\n",
            "test_cases": [
                {"input": f"Person{problem_id} {170 + problem_id} {65.5 + problem_id}", "output": f"Person{problem_id}의 키는 {170 + problem_id}cm이며, 몸무게는 {65.5 + problem_id:.1f}kg입니다."}
            ]
        }

def generate_problem_by_chapter(chapter_name, problem_id, difficulty):
    """단원별로 문제 생성"""
    generators = {
        "출력": generate_output_problem,
        "변수와 입력": generate_variable_input_problem,
        "연산자": generate_operator_problem,
        "문자열1": generate_string1_problem,
    }
    
    generator = generators.get(chapter_name)
    if generator:
        return generator(problem_id, difficulty)
    
    # 기본 템플릿 (다른 단원들은 나중에 Gemini API로 생성)
    return {
        "title": f"{chapter_name} 문제 {problem_id}",
        "description": f"{chapter_name} 단원의 {problem_id}번 문제입니다. 이 문제는 Gemini API를 사용하여 생성해야 합니다.",
        "default_code": "# 여기에 코드를 작성하세요\n",
        "test_cases": [{"input": "", "output": ""}]
    }

def fill_problems_file(filepath):
    """문제 파일의 빈 템플릿을 실제 문제로 채움"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chapter_name = data['chapter_name']
    problems = data['problems']
    
    updated_count = 0
    for problem in problems:
        # 템플릿 문제인지 확인
        desc = problem.get('description', '')
        if "Gemini API를 사용하여 생성해야 합니다" in desc or not desc.strip() or desc == f"{chapter_name} 단원의 {problem.get('id')}번 문제입니다.":
            problem_id = problem['id']
            difficulty = get_difficulty(problem_id)
            
            # 실제 문제 내용 생성
            new_content = generate_problem_by_chapter(chapter_name, problem_id, difficulty)
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
    
    print("\n일부 단원은 기본 템플릿만 생성되었습니다. generate_problems_gemini.py를 사용하여 더 풍부한 문제를 생성할 수 있습니다.")

if __name__ == "__main__":
    main()

