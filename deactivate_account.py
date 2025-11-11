class deactivate_user():
    def deactivate_user(conn, email):
        """
        Deactivate a user account by setting is_active to 0.
        args:
            conn: db connection object
            email: the user's email address
            """

        try:
            cursor = conn.cursor()

            # check if the user exits
            cursor.execute("SELECT * FROM users WHERE email = ?", (email))
            user = cursor.fetchone()

            if not user:
                print(f "No user found with email: {email}")
                return

            # deactivate user
            cursor.execute(
                "UPDATE users SET is_active = 0 WHERE email = ?", (email,))
            conn.commit()
            print(f"User '{email}' has been deactivated successfully.")

        except sqlite3.Error as e:
            print(f"Database error while deactivating user: {e}")

    def reactivate_user(conn, email):
        """
        Reactivate a user account by setting is_active to 0.
        args:
            conn: db connection object
            email: the user's email address
            """

        try:
            cursor = conn.cursor()

            # check if the user exits
            cursor.execute("SELECT * FROM users WHERE email = ?", (email))
            user = cursor.fetchone()

            if not user:
                print(f "No user found with email: {email}")
                return

            # deactivate user
            cursor.execute(
                "UPDATE users SET is_active = 1 WHERE email = ?", (email,))
            conn.commit()
            print(f"User '{email}' has been reactivated successfully.")

        except sqlite3.Error as e:
            print(f"Database error while reactivating user: {e}")
