from datetime import datetime
from modules.database.models.User import User


class Database:
    @staticmethod
    def _get_user_id_and_name(message):
        user_id = message.chat.id
        if message.chat.type == "private":
            name = message.chat.first_name
        elif message.chat.type in ["group", "supergroup", "channel"]:
            name = message.chat.title
        return user_id, name

    @classmethod
    def check_user(cls, session, message):
        user_id, name = cls._get_user_id_and_name(message)
        now = datetime.now()

        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.last_seen_date = now
        else:
            user = User(
                id=user_id,
                username=name,
                coming_date=now,
                last_seen_date=now,
                is_admin=False,
                faceit_id=None,
            )
            session.add(user)
        session.commit()

    @classmethod
    def set_faceit_userid(cls, session, message, set_user_id=None, set_user_name=None, get_faceit_id=False):
        user_id = message.chat.id
        cls.check_user(session, message)

        user = session.query(User).filter_by(id=user_id).first()
        if set_user_id and set_user_name:
            user.faceit_id = set_user_id
            user.faceit_username = set_user_name
        session.commit()

        return user.faceit_id if get_faceit_id else bool(user.faceit_id)

    @staticmethod
    def get_user(session, message):
        return session.query(User).filter_by(id=message.chat.id).first()

    @classmethod
    def change_lang(cls, session, message, lang="en"):
        cls.check_user(session, message)
        user = session.query(User).filter_by(id=message.chat.id).first()
        user.lang = lang
        session.commit()

    @classmethod
    def get_lang(cls, session, message):
        cls.check_user(session, message)
        user = session.query(User).filter_by(id=message.chat.id).first()
        return user.lang if user else "en"
