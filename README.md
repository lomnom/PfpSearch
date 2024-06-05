# PfpSearch, a bot to search for reddit users with a specific profile picture.
## What it does
- Given an input image and subreddit, `Search.py` will scrape a subreddit for users, then compare the profile icon of these users to the input image. It will then use the SIFT algorithm to decide how similar the profile icon is to the input image, and generate an output file with similarities. 
- This output file can then be analysed with `Results.py` to find users with an icon that are most similar to the input.

## Installation
1. Install opencv2. Every platform has their own quirks.
2. install this and dependencies.
```bash
git clone https://github.com/lomnom/PfpSearch/
cd PfpSearch
git clone https://github.com/lomnom/Terminal/
mv Terminal/Term*.py .
rm -rf Terminal
pip3 install pyyaml
pip3 install asyncprawcore==2.4.0
pip3 install asyncpraw==7.7.0
```

## Setup
1. Go to https://www.reddit.com/prefs/apps and create a bot client id and secret
2. Add it to `cfg.yaml` as 
```yaml
client_id: <INSERT HERE
client_secret: <INSERT HERE
```

## Usage
### Search
1. Run `Search.py`
2. Enter the subreddit to scrape from (eg. `memes`)
3. Enter the output file (eg. `Results.txt`)
4. Enter the image (eg. `/home/lomnom/Desktop/me.png`) or the username (eg. `u/spez`) to match against
5. Let it run. Stop everyone on the same network from using reddit for maximum scraping.
6. When the bot says `Request error!! Resting for 3 mins.` three times in a row, it has ended. `ctrl+c` twice to exit the program.

### Input image requirements:
- Crop out everything that is not the icon
- Mirror the image if needed to ensure snoo is facing right
- Dark mode images work best. Light mode images will be much more innacurate.

### Results analysis
- First,
1. Run `Results.py`
2. Enter the output file (eg. `Results.txt`)
3. Press enter to skip the positve prompt.
3. The best results are at the bottom and the worst at the top. The `[⢄⣆⢚⣋⢷⡝⠔⠈]` braille diagram summarises the image similarity. Images with the same diagram are likely to be the same. The similarity percentages are listed from smallest to biggest, with the colour getting lighter as it increases.
4. The top result is usually a false positive. Check to about the 80th percentile of results. Once you find a good result, copy its braille diagram.

- Then,
1. Run `Results.py`
2. Enter the output file (eg. `Results.txt`)
3. Enter the positive braille diagram (eg. `⢄⣆⢚⣋⢷⡝⠔⠈` no brackets) or its trait list (eg. `1,2,6,7,` with trailing comma) 
4. The closest result will be listed at the bottom and the worst one on the top. The value in `d=N` is the difference from the positive result and that listed result.
5. These are the real results with false positives weeded out.

## Caveats
- Because of a bug in PRAW, a cursed workaround for 429 errors was implemented. As a result, the bot can only evaluate ~2100 users before being deauthenticated from reddit.
	- This means that the bot will not terminate cleanly, and needs the user to manually `ctrl-c` it.
	- The bot will run longer if noone on the same network is using reddit. This reduces the frequency of 429s for some reason.
	- The bot will crash after looking at every comment up to ~6 days into the past for medium-sized communities
- The SIFT algorithm will have a bias towards more detailed pfps, which causes some false positives that have higher similarity percentages than the actual true matches. Be sure to also check results from the ~80th percentile, the 100th percentile often is just a false positive.