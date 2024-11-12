# CS Comment Translator

Python code that translates English comments within C# code into Japanese.
I think it may be meaningless for those whose native language is not Japanese.

このツールは、C#コード内の英語コメントを日本語に翻訳するPythonスクリプトです。DeepL API（フリープラン）を利用して、コメントを翻訳します。

## 概要

このスクリプトは、指定したフォルダ内のC#ファイルに含まれる英語のコメントを自動的に日本語に翻訳します。サブフォルダ内のファイルも処理することができます。処理後、翻訳されたコメントは元のC#ファイルに上書きされ、バックアップが作成されます。

## 必要な準備

1. **DeepL APIキーの取得**  
   DeepL APIを使用するには、[DeepLの公式サイト](https://www.deepl.com/pro)でAPIキーを取得してください。フリープランを利用する場合は、そのAPIキーを`api_key.txt`ファイルに記載してください。

2. **APIの設定**  
   DeepL API以外のサービスを使用する場合は、`translate.py`の中のURLを変更してください。

## 使用方法

1. **Python環境の準備**  
   このスクリプトを実行するためには、`requests` ライブラリが必要です。以下のコマンドでインストールできます。

   ```bash
   pip install requests
   ```

2. **スクリプトの実行**  
   以下のコマンドを使用して、C#ファイルが格納されたフォルダを指定して実行します。

   ```bash
   python3 CS_comment_translator.py "フォルダのパス"
   ```

   上記のコマンドを実行すると、指定したフォルダ内のC#ファイルが処理され、コメントが翻訳されます。

### オプション引数

- `--include_subfolders`  
  サブフォルダ内のC#ファイルも含めて処理します。

- `--char_count_only`  
  翻訳リクエストを送信せず、翻訳対象の文字数のみをカウントします。DeepL APIの月ごとの文字数制限を超えていないか確認するために、事前に確認することをおすすめします。

  ```bash
  python3 CS_comment_translator.py "フォルダのパス" --char_count_only
  ```

### 処理の流れ

1. 指定したフォルダ内のC#ファイルを読み込み、コメントを抽出します。
2. 抽出した英語コメントをDeepL APIを使用して日本語に翻訳します。
3. 翻訳されたコメントでC#ファイルを更新します。
4. 更新前のファイルは`backup`フォルダにバックアップとして保存されます。

## 注意事項

- DeepL APIフリープランには月間文字数制限があります。使用前に制限を確認してください。
- APIキーは`api_key.txt`に保存し、適切に管理してください。
- その他、DeepL APIの利用規約については公式サイトで確認してください。