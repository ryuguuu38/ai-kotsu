# -*- coding: utf-8 -*-
"""公開してはいけない言葉の一覧（点検ツール check_site.py と、集める側 collect_sources.py で共通に使う）。
このリポジトリは公開なので、個人・勤め先が特定できる語と、手元のパソコンの情報を弾く。
※「オーナー指定」は画面に出す正常なラベルなので対象外。
"""
PRIVATE_WORDS = ["apol.co.jp", "@apol", "アポロ株式会社", "山\u5c4e", "yamasaki", "ryuichi.yamasaki",
                 "/Users/", "あなたの社内ルール", "弊社は研修会社"]
