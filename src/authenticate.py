from db_connect import get_connection

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, password FROM account WHERE email = %s",
        (email,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        db_password = result[1]

        if db_password == password:
            return result[0]

    return None

def change_password(email, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
        "UPDATE account SET password = %s WHERE email = %s",(new_password,email))

        conn.commit() #luu thay doi vao db

        return True
    except Exception as e:
        conn.rollback() #huy thay doi
        return False, str(e)
    
def change_email(old_email, new_email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
        "UPDATE account SET email = %s WHERE email = %s",(new_email,old_email))

        conn.commit() #luu thay doi vao db

        return True
    except Exception as e:
        conn.rollback() #huy thay doi
        return False, str(e)