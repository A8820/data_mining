from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import task_lesson3_meta
from task_lesson3_meta import Base, Posts, Writers, Tags, Comments


class DataBase:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    @staticmethod
    def _get_or_create(session, model, **data):
        db_model = session.query(model).filter(model.url == data['url']).first()
        if not db_model:
            db_model = task_lesson3_meta

        return db_model

    def create_post(self, data):
        session = self.maker()
        tags = map(lambda tag_data: self._get_or_create(session, Tags['url'], **tag_data), data['tags'])
        comments = map(lambda comment_data: self._get_or_create(session, Comments['url'], **comment_data),
                       data['comments'])
        writer = self._get_or_create(session, Writers, **data['writer'])
        post = self._get_or_create(session, Posts, **data['post_data'], writer=writer)
        post.tags.extend(tags)
        post.comments.extend(comments)
        session.add(post)

        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()
        print(1)
