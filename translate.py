import requests

def load_api_key():
    api_key_file = 'api_key.txt'  # APIキーを保存したテキストファイルのパス
    with open(api_key_file, 'r') as file:
        return file.read().strip()

def main(text, source_lang = 'EN', target_lang = 'JA'):
    api_key = load_api_key()
    # パラメータの指定
    params = {
                'auth_key' : api_key,
                'text' : text,
                'source_lang' : source_lang, # 翻訳対象の言語
                "target_lang": target_lang  # 翻訳後の言語
            }

    # リクエストを投げる
    request = requests.post("https://api-free.deepl.com/v2/translate", data=params) # URIは有償版, 無償版で異なるため要注意
    result = request.json()
    print(result['translations'][0]['text'])
    return result['translations'][0]['text']

def main_dummy(text, source_lang = 'EN', target_lang = 'JA'):
    #print(text)
    return "ダミーの翻訳結果ですよ、ほんとは翻訳してませんよ、ほんとですよ、祖父母の家に行くときには、いつもお菓子を持っていくといいですよ"


if __name__ == '__main__':
    text = 'Returns <see langword="true"/> if the spawner successfully spawned an object. Otherwise returns <see langword="false"/>, for instance if the spawn point is out of view of the camera.'
    result = main(text, 'EN', 'JA') # 英語から日本語へ翻訳
    print(result)
