import json
from django.core.management.base import BaseCommand
from django.db import transaction
from questions.models import Subject, Question

class Command(BaseCommand):
    help = 'Populates the database with 50 Python programming questions for Subject ID 2.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting to populate Python questions..."))

        try:
            subject = Subject.objects.get(pk=2)
            self.stdout.write(f"Found subject: '{subject.name}'")
        except Subject.DoesNotExist:
            self.stderr.write(self.style.ERROR("Subject with ID=2 (Python程式設計基礎) not found. Aborting."))
            return

        python_questions = [
            # 1-10: Basic Syntax & Data Types
            {'content': '在Python中，哪個關鍵字用於定義一個函數？', 'options': {'A': 'func', 'B': 'def', 'C': 'function', 'D': 'define'}, 'correct_answer': 'B', 'explanation': '`def` 是Python中用來定義函數的關鍵字。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '下列哪個是Python中的浮點數類型？', 'options': {'A': 'int', 'B': 'str', 'C': 'float', 'D': 'bool'}, 'correct_answer': 'C', 'explanation': '`float` 用於表示帶有小數點的數字。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '`x = 5` 在Python中代表什麼操作？', 'options': {'A': '比較', 'B': '賦值', 'C': '轉換', 'D': '刪除'}, 'correct_answer': 'B', 'explanation': '單個等號 `=` 是賦值運算符。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '如何獲取字符串 `s = "Hello, World!"` 的長度？', 'options': {'A': 's.length()', 'B': 'len(s)', 'C': 's.size()', 'D': 'length(s)'}, 'correct_answer': 'B', 'explanation': '`len()` 是一個內置函數，用於返回對象的長度。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': 'Python中的布林類型 `bool` 有哪些值？', 'options': {'A': 'True, False', 'B': 'Yes, No', 'C': '1, 0', 'D': 'T, F'}, 'correct_answer': 'A', 'explanation': 'Python的布林值是 `True` 和 `False`。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': 'Python中使用 _____ 符號來表示單行註釋。', 'options': {}, 'correct_answer': '#', 'explanation': '井號 `#` 用於標記單行註釋的開始。', 'difficulty': 'easy', 'question_type': 'fill_in_blank'},
            {'content': '`10 // 3` 的計算結果是什麼？', 'options': {'A': '3.33', 'B': '3', 'C': '4', 'D': '1'}, 'correct_answer': 'B', 'explanation': '`//` 是整除運算符，它返回除法結果的整數部分。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '哪個數據類型是不可變的 (immutable)？', 'options': {'A': 'list', 'B': 'dict', 'C': 'tuple', 'D': 'set'}, 'correct_answer': 'C', 'explanation': '元組 `tuple` 一旦創建就不能被修改。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`"Python"[1:4]` 的輸出結果是什麼？', 'options': {'A': '"yth"', 'B': '"pyt"', 'C': '"ytho"', 'D': '"tho"'}, 'correct_answer': 'A', 'explanation': '字符串切片包含起始索引，但不包含結束索引。所以它會返回索引1, 2, 3的字符。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '如何將數字 `5` 轉換為字符串？', 'options': {'A': 'string(5)', 'B': 'str(5)', 'C': 'parse.string(5)', 'D': 'to_string(5)'}, 'correct_answer': 'B', 'explanation': '`str()` 函數可以將其他類型的對象轉換為字符串。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            
            # 11-20: Operators & Control Flow
            {'content': '`x = 10; y = 5; x % y` 的結果是什麼？', 'options': {'A': '2', 'B': '0', 'C': '5', 'D': '1'}, 'correct_answer': 'B', 'explanation': '`%` 是模數運算符，返回除法的餘數。10除以5的餘數是0。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '哪個運算符用於檢查兩個值是否相等？', 'options': {'A': '=', 'B': '!=', 'C': '==', 'D': '<>'}, 'correct_answer': 'C', 'explanation': '雙等號 `==` 用於比較兩個值是否相等。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '`if x > 10: ...` 之後，哪個關鍵字用於處理不滿足if條件的情況？', 'options': {'A': 'or', 'B': 'then', 'C': 'else', 'D': 'except'}, 'correct_answer': 'C', 'explanation': '`else` 語句用於執行if條件為False時的代碼塊。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '哪個循環會在條件為真時一直執行？', 'options': {'A': 'for', 'B': 'if', 'C': 'while', 'D': 'loop'}, 'correct_answer': 'C', 'explanation': '`while` 循環只要其條件保持為真，就會持續執行。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '`for i in range(3): print(i)` 的輸出是什麼？', 'options': {'A': '1 2 3', 'B': '0 1 2', 'C': '0 1 2 3', 'D': '1 2'}, 'correct_answer': 'B', 'explanation': '`range(3)` 會生成從0到2的數字序列。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`and`, `or`, `not` 是Python中的什麼運算符？', 'options': {'A': '算術運算符', 'B': '比較運算符', 'C': '邏輯運算符', 'D': '賦值運算符'}, 'correct_answer': 'C', 'explanation': '它們是用於組合條件語句的邏輯運算符。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '`elif` 關鍵字的作用是什麼？', 'options': {'A': '結束循環', 'B': '如果前一個if為False，則檢查新的條件', 'C': '定義一個函數', 'D': '捕獲異常'}, 'correct_answer': 'B', 'explanation': '`elif` 是 "else if" 的縮寫，用於在前一個if或elif條件不成立時，檢查另一個條件。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`break` 語句在循環中的作用是什麼？', 'options': {'A': '跳過當前迭代，進入下一次迭代', 'B': '完全終止循環', 'C': '暫停循環', 'D': '引發一個錯誤'}, 'correct_answer': 'B', 'explanation': '`break` 用於立即退出當前所在的循環。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`continue` 語句在循環中的作用是什麼？', 'options': {'A': '完全終止循環', 'B': '跳過當前迭代的剩餘部分，直接進入下一次迭代', 'C': '重新開始整個循環', 'D': '什麼都不做'}, 'correct_answer': 'B', 'explanation': '`continue` 用於跳過本次循環中剩餘的代碼，直接開始下一次循環。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`5 ** 2` 的結果是什麼？', 'options': {'A': '10', 'B': '7', 'C': '25', 'D': '3'}, 'correct_answer': 'C', 'explanation': '`**` 是指數運算符，表示5的2次方。', 'difficulty': 'easy', 'question_type': 'single_choice'},

            # 21-30: Data Structures (List, Tuple, Dict, Set)
            {'content': '哪個是Python中創建列表的正確語法？', 'options': {'A': '()', 'B': '{}', 'C': '[]', 'D': '<>'}, 'correct_answer': 'C', 'explanation': '列表使用方括號 `[]` 創建。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '如何向列表 `my_list` 的末尾添加元素 `x`？', 'options': {'A': 'my_list.add(x)', 'B': 'my_list.push(x)', 'C': 'my_list.append(x)', 'D': 'my_list.insert(x)'}, 'correct_answer': 'C', 'explanation': '`append()` 方法用於在列表末尾添加一個元素。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '在字典中，數據是以什麼形式存儲的？', 'options': {'A': '索引-值對', 'B': '鍵-值對', 'C': '名稱-值對', 'D': '元素序列'}, 'correct_answer': 'B', 'explanation': '字典存儲的是鍵(key)和值(value)的映射。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '`my_dict = {"name": "Alice", "age": 25}`，如何獲取 "Alice" 這個值？', 'options': {'A': 'my_dict[0]', 'B': 'my_dict.get("name")', 'C': 'my_dict.value("name")', 'D': 'my_dict["name"]'}, 'correct_answer': 'D', 'explanation': '可以使用鍵 `["name"]` 來訪問字典中對應的值。`get("name")` 也可以，但 `D` 是更直接的選項。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '集合 `set` 數據類型的最主要特點是什麼？', 'options': {'A': '元素有序且可重複', 'B': '元素無序且可重複', 'C': '元素無序且唯一', 'D': '元素有序且唯一'}, 'correct_answer': 'C', 'explanation': '集合中的元素是無序的，並且每個元素都是唯一的，不允許重複。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`my_list = [1, 2, 3]`，`my_list[1]` 的值是什麼？', 'options': {'A': '1', 'B': '2', 'C': '3', 'D': '錯誤'}, 'correct_answer': 'B', 'explanation': 'Python的列表索引是從0開始的，所以索引1對應的是第二個元素。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '如何從列表 `my_list` 中移除第一個出現的元素 `x`？', 'options': {'A': 'my_list.delete(x)', 'B': 'my_list.pop(x)', 'C': 'my_list.remove(x)', 'D': 'my_list.discard(x)'}, 'correct_answer': 'C', 'explanation': '`remove()` 方法用於移除列表中第一個匹配的元素值。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '元組 `my_tuple = (1, 2, 3)` 和列表 `my_list = [1, 2, 3]` 的主要區別是什麼？', 'options': {'A': '元組是有序的，列表是無序的', 'B': '元組是不可變的，列表是可變的', 'C': '元組只能存數字，列表可以存任何類型', 'D': '沒有區別'}, 'correct_answer': 'B', 'explanation': '元組是不可變的（immutable），創建後不能修改；而列表是可變的（mutable）。', 'difficulty': 'hard', 'question_type': 'single_choice'},
            {'content': '下列哪些是Python的內置數據結構？', 'options': {'A': 'List', 'B': 'Dictionary', 'C': 'Tuple', 'D': 'Array'}, 'correct_answer': '["A", "B", "C"]', 'explanation': 'List, Dictionary, Tuple, 和 Set 都是Python內置的數據結構。Array需要從 `array` 模塊導入。', 'difficulty': 'medium', 'question_type': 'multiple_choice'},
            {'content': '要創建一個空集合，應該使用哪個語法？', 'options': {'A': '{}', 'B': '[]', 'C': '()', 'D': 'set()'}, 'correct_answer': 'D', 'explanation': '直接使用 `{}` 會創建一個空字典，要創建空集合必須使用 `set()`。', 'difficulty': 'hard', 'question_type': 'single_choice'},

            # 31-40: Functions & Scope
            {'content': '在函數內部定義的變量稱為什麼？', 'options': {'A': '全局變量', 'B': '局部變量', 'C': '靜態變量', 'D': '實例變量'}, 'correct_answer': 'B', 'explanation': '在函數內部定義的變量作用域僅限於該函數，稱為局部變量。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': 'Python中，`*args` 在函數定義中的作用是什麼？', 'options': {'A': '接收任意數量的關鍵字參數', 'B': '接收一個元組形式的參數', 'C': '接收任意數量的位置參數', 'D': '表示一個指針'}, 'correct_answer': 'C', 'explanation': '`*args` 用於將任意數量的位置參數打包成一個元組。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': 'Python中，`**kwargs` 在函數定義中的作用是什麼？', 'options': {'A': '接收任意數量的關鍵字參數', 'B': '接收一個列表形式的參數', 'C': '接收任意數量的位置參數', 'D': '表示二級指針'}, 'correct_answer': 'A', 'explanation': '`**kwargs` 用於將任意數量的關鍵字參數打包成一個字典。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`lambda` 關鍵字用於做什麼？', 'options': {'A': '創建一個生成器', 'B': '定義一個標準函數', 'C': '創建一個匿名函數', 'D': '導入一個模塊'}, 'correct_answer': 'C', 'explanation': '`lambda` 用於創建簡單的、單行的匿名函數。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '如果一個函數沒有 `return` 語句，它默認返回什麼？', 'options': {'A': '0', 'B': 'None', 'C': 'True', 'D': '空字符串'}, 'correct_answer': 'B', 'explanation': '所有沒有顯式返回值的函數都會隱式返回 `None`。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '如何在函數內部修改一個全局變量 `x`？', 'options': {'A': '直接賦值 `x = 10`', 'B': '使用 `global x` 關鍵字', 'C': '使用 `modify x`', 'D': '無法修改'}, 'correct_answer': 'B', 'explanation': '必須先使用 `global` 關鍵字聲明，才能在函數內部修改全局變量的值。', 'difficulty': 'hard', 'question_type': 'single_choice'},
            {'content': '`map(function, iterable)` 函數的作用是什麼？', 'options': {'A': '將 `function` 應用於 `iterable` 的每個元素，並返回一個迭代器', 'B': '過濾 `iterable` 中不符合 `function` 條件的元素', 'C': '將 `iterable` 轉換為地圖', 'D': '遍歷 `iterable`'}, 'correct_answer': 'A', 'explanation': '`map()` 會對序列的每個項目執行一個函數。', 'difficulty': 'hard', 'question_type': 'single_choice'},
            {'content': '遞歸函數是指什麼？', 'options': {'A': '調用其他模塊的函數', 'B': '在循環中運行的函數', 'C': '可以自己調用自己的函數', 'D': '沒有返回值的函數'}, 'correct_answer': 'C', 'explanation': '遞歸函數是一種在其定義中直接或間接調用自身的函數。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '函數的文檔字符串 (docstring) 是什麼？', 'options': {'A': '函數的第一個註釋行', 'B': '函數定義後緊跟的第一個字符串字面量', 'C': '函數的返回類型說明', 'D': '函數的參數列表'}, 'correct_answer': 'B', 'explanation': '文檔字符串是用於解釋函數功能的字符串，可以通過 `help(function)` 或 `function.__doc__` 查看。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`print()` 是一個 _____ 函數。', 'options': {}, 'correct_answer': '內置', 'explanation': '`print()` 是Python提供的內置函數之一，無需導入即可使用。', 'difficulty': 'easy', 'question_type': 'fill_in_blank'},
            
            # 41-50: Modules, Exceptions & Files
            {'content': '哪個關鍵字用於導入Python模塊？', 'options': {'A': 'include', 'B': 'import', 'C': 'require', 'D': 'use'}, 'correct_answer': 'B', 'explanation': '`import` 語句用於導入其他Python文件或庫。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '處理可能引發錯誤的代碼塊，應該使用哪個語句？', 'options': {'A': 'try...except', 'B': 'if...else', 'C': 'do...while', 'D': 'check...error'}, 'correct_answer': 'A', 'explanation': '`try...except` 塊用於捕獲和處理異常。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '`finally` 塊在 `try...except` 結構中的作用是什麼？', 'options': {'A': '只在發生錯誤時執行', 'B': '只在沒有錯誤時執行', 'C': '無論是否發生錯誤，總會執行', 'D': '定義最終的錯誤類型'}, 'correct_answer': 'C', 'explanation': '`finally` 中的代碼無論異常是否發生，都會在離開try塊之前執行，通常用於清理資源。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '打開文件進行寫入操作，如果文件不存在會發生什麼？', 'options': {'A': '引發錯誤', 'B': '創建一個新文件', 'C': '什麼都不做', 'D': '詢問用戶'}, 'correct_answer': 'B', 'explanation': '在寫入模式（`w`）下，如果文件不存在，Python會自動創建它。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`with open("file.txt", "r") as f:` 這種寫法的好處是什麼？', 'options': {'A': '速度更快', 'B': '自動處理文件關閉', 'C': '可以讀取任何文件類型', 'D': '語法更短'}, 'correct_answer': 'B', 'explanation': '使用 `with` 語句可以確保文件在代碼塊執行完畢後，即使發生錯誤，也會被正確關閉。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '`json` 模塊主要用於做什麼？', 'options': {'A': '處理日期和時間', 'B': '數學運算', 'C': '解析和生成JSON格式的數據', 'D': '操作操作系統'}, 'correct_answer': 'C', 'explanation': '`json` 模塊提供了在Python對象和JSON字符串之間進行轉換的功能。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '`raise` 關鍵字的作用是什麼？', 'options': {'A': '捕獲一個異常', 'B': '打印一個錯誤信息', 'C': '手動引發一個異常', 'D': '忽略一個異常'}, 'correct_answer': 'C', 'explanation': '`raise` 用於在代碼中主動觸發一個指定類型的異常。', 'difficulty': 'hard', 'question_type': 'single_choice'},
            {'content': '若要從 `math` 模塊中只導入 `sqrt` 函數，應使用哪個語句？', 'options': {'A': 'import math.sqrt', 'B': 'import sqrt from math', 'C': 'from math import sqrt', 'D': 'using math.sqrt'}, 'correct_answer': 'C', 'explanation': '`from ... import ...` 語法用於從模塊中導入特定的變量或函數。', 'difficulty': 'medium', 'question_type': 'single_choice'},
            {'content': '哪個文件打開模式表示"追加"？', 'options': {'A': 'r', 'B': 'w', 'C': 'a', 'D': 'x'}, 'correct_answer': 'C', 'explanation': '模式 `a` (append) 會在文件末尾追加內容，而不會覆蓋原有內容。', 'difficulty': 'easy', 'question_type': 'single_choice'},
            {'content': '`pip` 是Python的 _____ 管理器。', 'options': {}, 'correct_answer': '包', 'explanation': 'pip 是推薦的用於安裝和管理Python包的工具。', 'difficulty': 'easy', 'question_type': 'fill_in_blank'},
        ]
        
        created_count = 0
        for q_data in python_questions:
            # For multiple choice, ensure correct_answer is a JSON string
            if q_data['question_type'] == 'multiple_choice':
                correct_answer = q_data['correct_answer']
            else:
                correct_answer = q_data['correct_answer']

            question, created = Question.objects.update_or_create(
                subject=subject,
                content=q_data['content'],
                defaults={
                    'options': q_data['options'],
                    'correct_answer': correct_answer,
                    'explanation': q_data.get('explanation', ''),
                    'question_type': q_data['question_type'],
                    'difficulty': q_data['difficulty'],
                    'is_ai_generated': True
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully populated the database. Created {created_count} new questions for subject '{subject.name}'.")) 