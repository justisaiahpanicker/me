import ollama


def generate_function():
    prompt = """
Write a Python function named is_prime(n).
Return True if n is prime, otherwise return False.
Numbers less than 2 are not prime.
Return only Python code, no Markdown or explanations.
"""

    response = ollama.generate(
        model="qwen2.5-coder:7b",
        prompt=prompt
    )

    code = response["response"]
    code = code.replace("```python", "")
    code = code.replace("```", "")

    return code.strip()


def test_function(code):
    namespace = {}
    passed = 0

    test_cases = [
        (2, True),
        (7, True),
        (4, False),
        (9, False),
        (1, False),
        (0, False),
        (-5, False)
    ]

    exec(code, namespace)
    function = namespace["is_prime"]

    for data, expected in test_cases:
        result = function(data)

        if result == expected:
            print(data, "PASS")
            passed += 1
        else:
            print(data, "FAIL")

    print(f"Passed: {passed}/{len(test_cases)}")

    if passed == len(test_cases):
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")


generated_code = generate_function()
print(generated_code)
test_function(generated_code)


import ollama
import ast


# 1. PROMPT
prompt = """def insertion_sort_function(arr):
    # Implement insertion sort manually
    return arr
"""

code = ""


# 2. GENERATE AND EXTRACT CODE
while True:
    response = ollama.chat(
        model="codegemma:2b",
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": 150}
    )

    raw = response["message"]["content"]
    cleaned = raw.replace("```python", "").replace("```", "")

    start = cleaned.find("def insertion_sort_function")

    if start != -1:
        code = cleaned[start:]
        end = code.find("return arr")

        if end != -1:
            code = code[:end + 10]

            if len(code) > 20 and "pass" not in code:
                break

    print("retrying")


# 3. DISPLAY GENERATED CODE
print("\n--- GENERATED CODE ---")
print(code)
print("----------------------")


# 4. FUNCTIONAL CHECK
passed = 0

test_cases = [
    ([3, 1, 2], [1, 2, 3]),
    ([1, 2, 3], [1, 2, 3]),
    ([3, 2, 1], [1, 2, 3]),
    ([2, 2, 1], [1, 2, 2]),
    ([-1, 0, -3], [-3, -1, 0]),
    ([1], [1]),
    ([], [])
]

try:
    namespace = {}
    exec(code, namespace)

    fn = namespace["insertion_sort_function"]

    for data, expected in test_cases:
        result = fn(data.copy())

        if result == expected:
            print(data, "PASS")
            passed += 1
        else:
            print(data, "FAIL")

    fnok = (passed == len(test_cases))

except Exception as e:
    print("Execution Error:", e)
    fnok = False

print(f"Passed: {passed}/{len(test_cases)}")


# 5. SYNTAX CHECK
try:
    ast.parse(code)
    synok = True
except SyntaxError:
    synok = False


# 6. BUILT-IN SORTING CHECK
algook = "sort(" not in code and "sorted(" not in code


# 7. FINAL RESULT
print("Functional:", fnok)
print("Syntax:", synok)
print("Algorithm:", algook)

if fnok and synok and algook:
    print("Score: 100/100")
    print("RESULT: ACCEPTED")
else:
    print("RESULT: REJECTED")

