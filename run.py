import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("TOKEN")

    if token:
        import bot

        bot.main(token)
    else:
        print("Expected TOKEN variable in environment, not found!")
