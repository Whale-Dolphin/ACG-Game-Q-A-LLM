import numpy

class Article:
    def __init__(self, game_id: int, post_id: int, f_forum_id: int, subject: str, url: str, text: str, created_at: int, like_num: int, length: int):
        self.game_id = game_id
        self.post_id = post_id
        self.f_forum_id = f_forum_id
        self.subject = subject
        self.url = url
        self.text = text
        self.created_at = created_at
        self.like_num = like_num
        self.length = length

class Vector_Paragraph(Article):
    def __init__(self, game_id: int, post_id: int, f_forum_id: int, subject: str, url: str, text: str, created_at: int, like_num: int, length: int, vector: numpy.ndarray):
        super().__init__(game_id, post_id, f_forum_id, subject, url, text, created_at, like_num, length)
        self.vector = vector
        self.text = text
        self.length = length