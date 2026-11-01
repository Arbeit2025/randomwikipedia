import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module  # noqa: E402

SAMPLE = {
    "title": "テスト記事",
    "description": "テスト用の説明",
    "extract": "これはテスト記事の概要です。",
    "thumbnail": "https://example.com/thumb.jpg",
    "url": "https://ja.wikipedia.org/wiki/テスト記事",
}


class RandomWikipediaTest(unittest.TestCase):
    def setUp(self):
        self.client = app_module.app.test_client()
        self._orig_fetch = app_module.fetch_random_article

    def tearDown(self):
        app_module.fetch_random_article = self._orig_fetch

    def test_healthz(self):
        res = self.client.get("/healthz")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "ok")

    def test_index_ok(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("ランダムWikipedia", body)
        self.assertIn("ランダムで記事を表示", body)

    def test_random_success(self):
        app_module.fetch_random_article = lambda: dict(SAMPLE)
        res = self.client.get("/random")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("テスト記事", body)
        self.assertIn("これはテスト記事の概要です。", body)
        self.assertIn("テスト用の説明", body)
        self.assertIn("https://example.com/thumb.jpg", body)
        self.assertIn("https://ja.wikipedia.org/wiki/テスト記事", body)
        self.assertIn("記事を読む", body)

    def test_random_success_without_thumbnail(self):
        article = dict(SAMPLE)
        article["thumbnail"] = ""
        article["description"] = ""
        app_module.fetch_random_article = lambda: article
        res = self.client.get("/random")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("テスト記事", body)
        self.assertNotIn("example.com/thumb.jpg", body)

    def test_random_failure_shows_error(self):
        def boom():
            raise RuntimeError("network down")

        app_module.fetch_random_article = boom
        res = self.client.get("/random")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("記事を取得できませんでした", body)
        self.assertIn("ランダムで記事を表示", body)


if __name__ == "__main__":
    unittest.main()
