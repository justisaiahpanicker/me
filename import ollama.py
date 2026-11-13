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



import ollama
import ast
import re


# 1. TEN REFERENCE PROGRAMS
real_code_dataset = [
"""def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
""",
"""def insertion_sort(arr):
    for i in range(1, len(arr)):
        j = i
        while j > 0 and arr[j] < arr[j - 1]:
            arr[j], arr[j - 1] = arr[j - 1], arr[j]
            j -= 1
    return arr
""",
"""def insertion_sort(arr):
    i = 1
    while i < len(arr):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        i += 1
    return arr
""",
"""def insertion_sort(arr):
    i = 1
    while i < len(arr):
        j = i
        while j > 0 and arr[j - 1] > arr[j]:
            arr[j - 1], arr[j] = arr[j], arr[j - 1]
            j -= 1
        i += 1
    return arr
""",
"""def insertion_sort(arr):
    for i in range(1, len(arr)):
        for j in range(i, 0, -1):
            if arr[j] < arr[j - 1]:
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
            else:
                break
    return arr
""",
"""def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        position = i
        for j in range(i - 1, -1, -1):
            if arr[j] <= key:
                break
            arr[j + 1] = arr[j]
            position = j
        arr[position] = key
    return arr
""",
"""def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr.pop(i)
        j = i
        while j > 0 and arr[j - 1] > key:
            j -= 1
        arr.insert(j, key)
    return arr
""",
"""def insertion_sort(arr):
    result = []
    for key in arr:
        j = len(result)
        while j > 0 and result[j - 1] > key:
            j -= 1
        result.insert(j, key)
    return result
""",
"""def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i
        while j > 0:
            if arr[j - 1] <= key:
                break
            arr[j] = arr[j - 1]
            j -= 1
        arr[j] = key
    return arr
""",
"""def insertion_sort(arr):
    for i, key in enumerate(arr.copy()):
        j = i
        while j > 0 and key < arr[j - 1]:
            arr[j] = arr[j - 1]
            j -= 1
        arr[j] = key
    return arr
"""
]

print("Reference programs:", len(real_code_dataset))
for reference in real_code_dataset:
    print(reference)


# 2. GENERATE CODE USING CODEGEMMA 2B
prompt = """# Complete insertion sort using loops and comparisons.
# Sort ascending without sort() or sorted(). End with return arr.
def insertion_sort(arr):
"""

response = ollama.generate(
    model="codegemma:2b",
    prompt=prompt,
    options={"num_predict": 500}
)

code = prompt + response["response"]
code = code.replace("```python", "").replace("```", "")

end = code.find("return arr")
if end != -1:
    code = code[:end + 10]

print("\nGenerated Code:")
print(code)


# 3. SYNTAX CHECK
try:
    ast.parse(code)
    synok = True
except SyntaxError:
    synok = False


# 4. FUNCTIONAL CHECK
test_cases = [
    ([3, 1, 2], [1, 2, 3]),
    ([1, 2, 3], [1, 2, 3]),
    ([3, 2, 1], [1, 2, 3]),
    ([2, 2, 1], [1, 2, 2]),
    ([-1, 0, -3], [-3, -1, 0]),
    ([1], [1]),
    ([], [])
]

passed = 0

try:
    namespace = {}
    exec(code, namespace)
    fn = namespace["insertion_sort"]

    for data, expected in test_cases:
        if fn(data.copy()) == expected:
            print(data, "PASS")
            passed += 1
        else:
            print(data, "FAIL")

    fnok = passed == len(test_cases)

except Exception as e:
    print("Execution Error:", e)
    fnok = False


# 5. BASIC ALGORITHM CHECK
algook = (
    "def insertion_sort" in code
    and ("for " in code or "while " in code)
    and ("<" in code or ">" in code)
    and ".sort(" not in code
    and "sorted(" not in code
)


# 6. SIMILARITY CHECK
tokens = set(re.findall(r"[a-zA-Z_]+", code.lower()))
best = 0

for reference in real_code_dataset:
    real = set(re.findall(r"[a-zA-Z_]+", reference.lower()))
    combined = tokens | real

    if combined:
        similarity = len(tokens & real) / len(combined)
        best = max(best, similarity)

similarity = best * 100


# 7. SCORE AND FINAL RESULT
score = 0

if synok:
    score += 20
    if fnok:
        score += 40
    if algook:
        score += 20
    score += similarity * 0.20

print(f"\nPassed: {passed}/{len(test_cases)}")
print("Syntax:", synok)
print("Functional:", fnok)
print("Algorithm:", algook)
print("Similarity:", round(similarity, 2), "%")
print("Score:", round(score, 2), "/100")

if score >= 80:
    print("RESULT: ACCEPTED")
else:
    print("RESULT: REJECTED")
