import configparser
import os
import praw
import shutil


def main():
    """Main entry point of the program."""
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(os.path.expanduser("~/.config/reddit-wall.conf"))

    reddit = praw.Reddit("reddit-wall")
    subs = reddit.subreddit('+'.join(config.options("Subreddits")))
    limit = int(config["Downloads"]["ImageLimit"])

    for submission in subs.hot(limit=limit):
        print(submission.title)


if __name__ == "__main__":
    # Check if the config file exists. If not, copy the default.
    config_path = os.path.join(os.path.expanduser('~'), ".config/reddit-wall.conf")
    if not os.path.exists(config_path):
        shutil.copyfile("../reddit-wall.conf", config_path)

    main()
