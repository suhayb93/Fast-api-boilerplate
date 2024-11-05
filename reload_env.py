from dotenv import load_dotenv
load_dotenv()


def reload_env():
    # Reload the .env file
    load_dotenv(override=True)
    print('env file is reloaded')


if __name__ == '__main__':
    reload_env()