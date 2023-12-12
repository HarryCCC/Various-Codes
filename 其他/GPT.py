import openai

openai.api_key = "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"

system_intel = "answer my questions as if you were an expert in the field."
prompt = "try expressing love to me without saying love. (word limit < 15)"
#prompt = "are you not gpt-4?  (word limit < 15)"

# 调用GPT-4 API的函数
def ask_GPT4(system_intel, prompt): 
    print("答案生成中...")
    result = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                 messages=[{"role": "system", "content": system_intel},
                                           {"role": "user", "content": prompt}])
    response_content = result['choices'][0]['message']['content']
    print(response_content)
 
# 调用函数
ask_GPT4(system_intel, prompt)
