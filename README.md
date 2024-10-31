# CS_comment_translator

Python code that translates English comments within C# code into Japanese.

英語で書かれてあるC#のコメントを日本語に翻訳するpythonコードです。
DeepLのAPIのフリープランのAPIを使用する想定です。
フォルダを指定して一括で複数のC#ファイルを処理します。

APIキーをご自身で用意して頂く必要があります。
api_key.txt の中身をあなたのAPIキーに置き換えてください。

DeepLのAPIのフリープラン以外を使用する場合は、translate.pyの中のURLを置き換えてください。
DeepLのAPIのフリープランの制限や規約などはご自身でよくご確認ください。