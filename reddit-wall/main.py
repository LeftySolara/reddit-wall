import configparser
import os
import praw
import shutil


def get_subreddits(config, reddit):
    """Get the list of subreddits from the given config.
    
    Parameters
    ----------
    config : configparser.ConfigParser
        The configuration to check.
        
    reddit : praw.Reddit
        The reddit instance used to gather data.

    Returns
    -------
    subreddits : set
        Set of subreddit names.

    """

    subreddits = config.options("Subreddits")
    for sub in subreddits:
        sub = sub.lower()

    multi_config = config.options("Multireddits")
    multi_list = [tuple(m.split()) for m in multi_config]

    for user, multi in multi_list:
        multireddit = reddit.multireddit(user, multi)
        for sub in multireddit.subreddits:
            subreddits.append(sub.display_name.lower())

    subreddits = set(subreddits)
    return subreddits


def main():
    """Main entry point of the program."""

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(os.path.expanduser("~/.config/reddit-wall.conf"))
    reddit = praw.Reddit("reddit-wall")

    subreddits = get_subreddits(config, reddit)
    subs = reddit.subreddit('+'.join(subreddits))
    limit = int(config["Downloads"]["ImageLimit"])

    for submission in subs.hot(limit=limit):
        print(submission.title)


if __name__ == "__main__":
    # Check if the config file exists. If not, copy the default.
    config_path = os.path.join(os.path.expanduser('~'), ".config/reddit-wall.conf")
    if not os.path.exists(config_path):
        shutil.copyfile("../reddit-wall.conf", config_path)

    main()
