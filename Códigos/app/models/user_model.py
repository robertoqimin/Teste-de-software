from app.database import get_connection


class UserModel:
    def find_by_email(self, email):
        query = """
            SELECT id, name, email, password_hash, created_at
            FROM users
            WHERE email = %s
            LIMIT 1
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                return cursor.fetchone()

    def create_user(self, name, email, password_hash):
        query = """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name, email, password_hash))
                return cursor.lastrowid
