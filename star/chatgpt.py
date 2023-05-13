from star.logger import logger
# chatGPT
import openai

#openai.api_key = "sk-**"
#openai.api_base = "https://www.***.com/v1"


def chatGPT(text):
    if len(text) == 0:
        return
    text = text.replace('\n', ' ').replace('\r', '').strip()
    logger.info(f'chatGPT Q: {text}')
    # res = ask(text)
    res = sdkgptplus(text)
    logger.info(f'chatGPT A: {res}')
    return res


def ask(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        # model="text-davinci-003",
        prompt=text.strip(),
        temperature=0.3,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    # 容错处理
    if 'choices' in response:
        if len(response['choices']) > 0:
            answer = response.choices[0].text.strip()
        else:
            answer = 'Opps sorry, you beat the AI this time'
    else:
        answer = 'Opps sorry, you beat the AI this time'

    return answer
    # return response.choices[0].text.strip()


async def sdkgptplus(query):
    ms = [{"role": "user", "content": f"{query}"}]
    completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo", messages=ms
    )
    message = (
        completion["choices"][0]
        .get("message")
        .get("content")
        .encode("utf8")
        .decode()
    )
    return message
