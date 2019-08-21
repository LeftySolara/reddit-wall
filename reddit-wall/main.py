import configparser
import os
import pathlib
import praw
import requests
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

    allow_nsfw = config["Downloads"].getboolean("AllowNSFW")
    subreddit_config = config.options("Subreddits")
    subreddits = []

    if not allow_nsfw:
        for subreddit in subreddit_config:
            sub = reddit.subreddit(subreddit)
            if not sub.over18:
                subreddits.append(sub.display_name)
    else:
        subreddits = subreddit_names

    for sub in subreddits:
        sub = sub.lower()


    multi_config = config.options("Multireddits")
    multi_list = [tuple(m.split()) for m in multi_config]

    for user, multi in multi_list:
        multireddit = reddit.multireddit(user, multi)
        if not allow_nsfw and multireddit.over_18:
            continue
        for sub in multireddit.subreddits:
            subreddits.append(sub.display_name.lower())

    subreddits = set(subreddits)
    return subreddits


def download_post_image(config, post):
    """Download the image associated with the given reddit post."""

    if post.is_self:
        return False

    # FIXME: Check file permissions when attempting to create directory
    output_dir = pathlib.Path(config["Downloads"]["OutputDirectory"]).expanduser()
    if str(output_dir) == '.':
        output_dir = pathlib.Path.cwd()  # Get the absolute path
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    image_types = (".png", ".jpg", ".jpeg", ".gif")
    if not post.url.endswith(image_types):
        return False

    filename_start = post.url.rfind('/')
    filename = post.url[filename_start:]

    output_path = str(output_dir) + filename

    with open(output_path, "wb") as handle:
        response = requests.get(post.url, stream=True)
        if not response.ok:
            print(response)
            return False
        
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

    return True


def main():
    """Main entry point of the program."""

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(os.path.expanduser("~/.config/reddit-wall.conf"))
    reddit = praw.Reddit("reddit-wall")

    subreddits = get_subreddits(config, reddit)
    subs = reddit.subreddit('+'.join(subreddits))
    limit = int(config["Downloads"]["PostLimit"])
    allow_nsfw = config["Downloads"].getboolean("AllowNSFW")

    # There doesn't seem to be a way to specify a nsfw filter for subs.hot(),
    # so we have to keep track of when we skip posts.
    posts = []
    for submission in subs.hot():
        if not allow_nsfw and submission.over_18:
            continue
        
        posts.append(submission)
        if len(posts) > limit:
            break

    for post in posts:
        download_post_image(config, post)


if __name__ == "__main__":
    # Check if the config file exists. If not, copy the default.
    config_path = os.path.join(os.path.expanduser('~'), ".config/reddit-wall.conf")
    if not os.path.exists(config_path):
        shutil.copyfile("../reddit-wall.conf", config_path)

    main()
