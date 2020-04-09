import twitter
import sys

if not twitter.tweet("テストツイートです"):
    print("Failed to tweet")
    sys.exit(1)
