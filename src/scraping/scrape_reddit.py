import os
from dotenv import load_dotenv
import praw
import json
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

print("Client ID:", os.getenv("REDDIT_CLIENT_ID"))
print("Client Secret:", os.getenv("REDDIT_CLIENT_SECRET"))
print("User Agent:", os.getenv("REDDIT_USER_AGENT"))

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
    raise Exception("Missing one or more Reddit API credentials in .env file")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def get_comment_data(comment, depth=0, max_depth=1):
    """
    Recursively get comment data up to max_depth.
    """
    if depth > max_depth or isinstance(comment, praw.models.MoreComments):
        return None

    comment_info = {
        "id": comment.id,
        "author": str(comment.author),
        "body": comment.body,
        "score": comment.score,
        "created_utc": comment.created_utc,
        "replies": []
    }

    # Recursively get replies if depth allows
    if comment.replies:
        for reply in comment.replies:
            reply_data = get_comment_data(reply, depth + 1, max_depth)
            if reply_data:
                comment_info["replies"].append(reply_data)

    return comment_info

def scrape_subreddit(subreddit_name, limit=100, max_comment_depth=1):
    subreddit = reddit.subreddit(subreddit_name)
    posts_data = []

    print(f"Scraping r/{subreddit_name} for top {limit} posts...")

    # Wrap the post iteration with tqdm for a progress bar
    for post in tqdm(subreddit.hot(limit=limit), total=limit, desc="Scraping posts"):
        post.comments.replace_more(limit=None)  # Load all comments

        comments_data = []
        for top_level_comment in post.comments:
            comment_data = get_comment_data(top_level_comment, depth=0, max_depth=max_comment_depth)
            if comment_data:
                comments_data.append(comment_data)

        post_info = {
            "id": post.id,
            "title": post.title,
            "score": post.score,
            "num_comments": post.num_comments,
            "created_utc": post.created_utc,
            "author": str(post.author),
            "url": post.url,
            "selftext": post.selftext,
            "comments": comments_data
        }
        posts_data.append(post_info)

    print(f"Scraped {len(posts_data)} posts from r/{subreddit_name} including comments")
    return posts_data

def save_to_json(data, filename, folder_name="scraped_data"):
    """
    Saves data to a JSON file within a specified folder.
    Creates the folder if it doesn't exist.
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")

    # Construct the full file path
    filepath = os.path.join(folder_name, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to: {filepath}")

if __name__ == "__main__":
    folder_name = "data/reddit_data"
    subreddit_name = "cars"
    # posts = scrape_subreddit(subreddit_name, limit=1000, max_comment_depth=1)

    # save_to_json(posts, f'reddit_{subreddit_name}_posts_with_comments.json', folder_name)
    # print(f'Saved {len(posts)} posts with comments from r/{subreddit_name}')


    # subreddit_name = "askcarsales"
    # posts = scrape_subreddit(subreddit_name, limit=1000, max_comment_depth=1)

    # save_to_json(posts, f'reddit_{subreddit_name}_posts_with_comments.json', folder_name)
    # print(f'Saved {len(posts)} posts with comments from r/{subreddit_name}')


    # subreddit_name = "mechanicadvice"
    # posts = scrape_subreddit(subreddit_name, limit=1000, max_comment_depth=1)

    # save_to_json(posts, f'reddit_{subreddit_name}_posts_with_comments.json', folder_name)
    # print(f'Saved {len(posts)} posts with comments from r/{subreddit_name}')


    # subreddit_name = "usedcars"
    # posts = scrape_subreddit(subreddit_name, limit=1000, max_comment_depth=1)

    # save_to_json(posts, f'reddit_{subreddit_name}_posts_with_comments.json', folder_name)
    # print(f'Saved {len(posts)} posts with comments from r/{subreddit_name}')


    # subreddit_name = "CarTalk"
    # posts = scrape_subreddit(subreddit_name, limit=1000, max_comment_depth=1)

    # save_to_json(posts, f'reddit_{subreddit_name}_posts_with_comments.json', folder_name)
    # print(f'Saved {len(posts)} posts with comments from r/{subreddit_name}')


    # subreddit_name = "CarQuestions"
    # posts = scrape_subreddit(subreddit_name, limit=1000, max_comment_depth=1)

    # save_to_json(posts, f'reddit_{subreddit_name}_posts_with_comments.json', folder_name)
    # print(f'Saved {len(posts)} posts with comments from r/{subreddit_name}')