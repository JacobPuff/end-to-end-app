from server_stuffs.scripts.password_hashing import pwd_context
import datetime

if __name__ == "__main__":
    start = datetime.datetime.now()
    pwd_context.hash("TesterinoPassword")
    end = (datetime.datetime.now() - start)
    print(end)
