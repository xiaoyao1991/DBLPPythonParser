import MySQLdb
import settings


class DB(object):
    def __init__(self):
        super(DB, self).__init__()
        db_settings = {
            'host': settings.HOST,
            'user': settings.USER,
            'passwd':   settings.PASSWD,
            'use_unicode': True,
            'charset': 'utf8',
            'db': settings.DB
        }

        self.conn = MySQLdb.connect(**db_settings)
        self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

    def dumps(self, record):
        # insert into paper table
        query = """
            INSERT INTO publications (pub_key, pub_type, editor, title, booktitle, pages, pub_year, address, journal, volume, number, pub_month, url, ee, cdrom, cite, publisher, note, crossref, isbn, series, school, chapter)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, record.data_tuple())
        pub_id = self.cursor.lastrowid
        self.conn.commit()

        # handle authors
        authors = record.fields['author']
        author_ids = []

        for author in authors:
            query = """
                SELECT id 
                from authors 
                where author = %s
            """
            self.cursor.execute(query, (author))
            author_id = self.cursor.fetchone()
            if author_id is None:
                query = """
                    INSERT INTO authors (author)
                    VALUES(%s)
                """
                self.cursor.execute(query, (author))
                author_ids.append(int(self.cursor.lastrowid))
                self.conn.commit()
            else:
                author_ids.append(int(author_id['id']))

        # insert author-publication-relations
        for author_id in author_ids:
            query = """
                INSERT INTO authors_publications(author_id, publication_id)
                VALUES(%s, %s)
            """
            try:
                self.cursor.execute(query, (author_id, pub_id))
                self.conn.commit()
            except:
                pass


    def close(self):
        self.conn.close()