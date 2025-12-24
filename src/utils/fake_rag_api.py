import json
from random import choice

def get_ans(query: str) -> str:
    with open(r"D:\Work\prompt evaluator dashboard\uploads\rag_responses.json", "r") as file:
        responses = json.load(file).get("responses", [])
    for resp in responses:
        if resp.get("question") == query:
            select = choice(["correct", "vague", "incorrect"])
            if select == "correct":
                ans = resp.get("correct", "")
            elif select == "vague":
                ans = resp.get("vague", "")      
            else:
                ans = resp.get("incorrect", "")   
            context = resp.get("context", "")
            return ans, context
        

            
            
