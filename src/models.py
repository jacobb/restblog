from errors import NotFound


class BlogEntry(object):

    def __init__(self, **kwargs):
        self.body = kwargs.get('body', '')
        self.title = kwargs.get('title', '')
        self.id = kwargs.get('id', None)

    @property
    def url(self):
        return "/entry/{}".format(self.id)

    @property
    def api_url(self):
        return "/api/{}".format(self.id)

    def save(self, db):
        if not self.title:
            raise ValueError("Title is required to save")

        if not self.body:
            raise ValueError("Body is required to save")

        if not self.id:
            self._insert_sql(db)
        else:
            self._update_sql(db)

    def _insert_sql(self, db):
        cursor = db.cursor()
        cursor.execute('insert into entries (title, body) values (?, ?)',
                 [self.title, self.body])
        self.id = cursor.lastrowid
        db.commit()
        return self.id

    def _update_sql(self, db):
        db.execute('UPDATE entries SET title=?, body=? WHERE id=?',
                 [self.title, self.body, self.id])
        db.commit()

    @classmethod
    def get(cls, db, blog_id):
        cur = db.execute(
            'select id, title, body from entries where id = ?',
            [blog_id]
        )
        row = cur.fetchone()
        if not row:
            raise NotFound
        blog_entry = cls(id=row[0], title=row[1], body=row[2])
        return blog_entry

    @classmethod
    def get_all(cls, db):
        cur = db.execute('select id, title, body from entries order by id desc')
        rows = cur.fetchall()
        entries = [
            cls(id=row[0], title=row[1], body=row[2])
            for row in rows
        ]
        return entries

    def to_dict(self):
        blog_dict = {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'url': self.url,
            'api_url': self.api_url,
        }
        return blog_dict

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<BlogEntry: {}: {}>".format(self.id, self.title)
