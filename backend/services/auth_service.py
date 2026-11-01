import os, hashlib, hmac, secrets
from sqlalchemy import text

def _hash_password(password):
    salt=secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310000)
    return "pbkdf2_sha256$310000$"+salt.hex()+"$"+digest.hex()

def _verify_password(password,stored):
    try:
        algorithm,iterations,salt_hex,digest_hex=stored.split("$")
        if algorithm!="pbkdf2_sha256": return False
        candidate=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt_hex),int(iterations)).hex()
        return hmac.compare_digest(candidate,digest_hex)
    except Exception: return False

def register_user(name,email,password):
    if len(password)<8: return {"status":"failed","message":"Password must contain at least 8 characters"}
    try:
        if os.getenv("DATABASE_URL","").startswith(("postgresql://","postgresql+psycopg://")):
            from database.postgres import get_engine
            with get_engine().begin() as conn:
                row=conn.execute(text("INSERT INTO users (name,email,password_hash) VALUES (:name,:email,:password) RETURNING user_id"),{"name":name,"email":email,"password":_hash_password(password)}).first()
                return {"status":"success","message":"Account created successfully","user_id":int(row[0])}
        from database.connection import get_connection
        conn=get_connection()
        if conn is None: return {"status":"failed","message":"Database connection failed"}
        cursor=conn.cursor()
        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",(name,email,_hash_password(password)))
        conn.commit(); uid=cursor.lastrowid
        return {"status":"success","message":"Account created successfully","user_id":uid}
    except Exception as exc: return {"status":"failed","message":str(exc)}
    finally:
        try: cursor.close(); conn.close()
        except Exception: pass

def login_user(email,password):
    try:
        if os.getenv("DATABASE_URL","").startswith(("postgresql://","postgresql+psycopg://")):
            from database.postgres import get_engine
            with get_engine().begin() as conn:
                row=conn.execute(text("SELECT user_id,name,email,password_hash FROM users WHERE email=:email"),{"email":email}).mappings().first()
                if not row or not _verify_password(password,row["password_hash"]): return {"status":"failed","message":"Invalid email or password"}
                return {"status":"success","message":"Login successful","user":{"user_id":row["user_id"],"name":row["name"],"email":row["email"]}}
        from database.connection import get_connection
        conn=get_connection()
        if conn is None: return {"status":"failed","message":"Database connection failed"}
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id,name,email,password FROM users WHERE email=%s",(email,)); row=cursor.fetchone()
        if not row: return {"status":"failed","message":"Invalid email or password"}
        stored=row.pop("password")
        if stored.startswith("pbkdf2_sha256$"):
            valid=_verify_password(password,stored)
        else:
            # One-time compatibility for existing plaintext legacy records; upgrade on successful login.
            valid=hmac.compare_digest(str(stored),password)
            if valid:
                cursor.execute("UPDATE users SET password=%s WHERE user_id=%s",(_hash_password(password),row["user_id"])); conn.commit()
        if not valid: return {"status":"failed","message":"Invalid email or password"}
        return {"status":"success","message":"Login successful","user":row}
    except Exception as exc: return {"status":"failed","message":str(exc)}
    finally:
        try: cursor.close(); conn.close()
        except Exception: pass
