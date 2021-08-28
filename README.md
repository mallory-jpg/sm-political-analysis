# Social Media Political Analysis 🇺🇸
### Springboard Open-ended Capstone
![SM Political Analysis - 4](https://user-images.githubusercontent.com/65197541/131225592-9e8dd0a0-1750-408f-93d8-72ca04e88e1a.png)
## Objectives
### Problems & Questions
_How can we better develop educational materials to meet kids where they are?_
* Is it worth it to spend money to advertise to youth for political campaigns - are they engaging with current events?
* What politics & policies are The Youth™ talking about & why?

### Goals
* to analyze how age/youth impacts political indoctrination and participation
* to track social impacts of political events
* to understand colloquial knowledge of political concepts

### Overview:
1. [x] Use NewsAPI to find top news by day
2. [x] Parse news story title & article into individual words/phrases
3. [x] Count most important individual words & phrases
4. [x]  Use top 3 most important words & phrases to search TikTok & Twitter
5. []  Count number of tweets & TikToks mentioning key words & phrases

## Installation & Use
`config.ini` should have the following layout and info:

  ```
  [database]
    host = <hostname>
    database = <db name>
    user = <db username>
    password = <db password>
  
  [newsAuth]
    api_key = <NewsAPI.org API key>

  [tiktokAuth]
    s_v_web_id = <s_v_web_id>

  [twitterAuth]
    access_token = <access_token>
    access_token_secret = <access_token_secret>
    consumer_key = <consumer_key>
    consumer_secret = <consumer_secret>
  ```
  *Note*: headers and keys/variables in config.ini file don't need to be stored as strings, but when calling them in program, enclose references with quotes

### To scrape the web without getting blocked:
Clone the following url into your project directory using Git or checkout with SVN: `https://github.com/tamimibrahim17/List-of-user-agents.git`. These .txt files contain User Agents and are specified by browser (shout out [Timam Ibrahim][https://github.com/tamimibrahim17]!). They will be randomized to avoid detection by web browsers.

### To find your `s_v_web_id` for TikTokAPI access:
1. Go to the TikTok website & login
2. If using Google Chrome, open the developer console 
3. Go to the 'Application' tab 
4. Find & click 'Cookies' in the left-hand panel → 
5. On the resulting screen, look for s_v_web_id under the 'name' column

Find more information about .ini configuration files in Python documentation: `https://docs.python.org/3/library/configparser.html`

## Exploratory Data Analysis

This step was guided by my anticipation that the data will be used for trend graphing, sentiment analysis, age inference, and correlation between user characteristics and extent of participation in responding to political events. With this in mind, I plan to optimize query speed via limiting storage by geographic location of both users and events to the US (though this categorization may be loose at times because of US involvement on the world stage). My PostgreSQL database will also be sharded by datetime, as the analytical window references 3 days before and 3 days after the political event of interest.

At this point, I've found that my GET requests for popular news articles return various formats which must be converted, unpacked, or otherwise transformed. Because of this added step, I opted to keep the article text in a separate table within the database. The text in this table will serve as data sources from which to extract our top 3 keywords (per article) using Term Frequency-Inverse Document Frequency (TF-IDF) calculations. These keywords will be applied to our searches for related TikToks and tweets. For some resources on this, check out
[TF-IDF in the real world](https://towardsdatascience.com/tf-idf-for-document-ranking-from-scratch-in-python-on-real-world-dataset-796d339a4089) and [a step-by-step guide by Prachi Prakash](https://www.analyticsvidhya.com/blog/2020/11/words-that-matter-a-simple-guide-to-keyword-extraction-in-python/).

With data from social media adding a pop-cultural context to political news, we inch closer to an understanding of TikTok and Twitter as novel forms of youth political engagement!

Check out this project's slide deck ⤵
![SM Political Analysis - 4 (2)](https://user-images.githubusercontent.com/65197541/131225593-367e0894-08d3-4fea-ab17-36f274e03c64.png)
![SM Political Analysis - 4 (4)](https://user-images.githubusercontent.com/65197541/131225599-038ec36c-d644-4f60-a8f2-0bd43ade94df.png)
![SM Political Analysis - 4 (7)](https://user-images.githubusercontent.com/65197541/131225638-ba49f6d7-a3e1-46bc-8b54-a71b319b8990.png)
![SM Political Analysis - 4 (8)](https://user-images.githubusercontent.com/65197541/131225639-88301e11-ed3c-4ab0-8b11-2cbd95d0677c.png)
![SM Political Analysis - 4 (9)](https://user-images.githubusercontent.com/65197541/131225641-d1427eb3-439e-4691-9f3d-9eb9b7cbc2b8.png)
![SM Political Analysis - 4 (10)](https://user-images.githubusercontent.com/65197541/131225642-20b9ca15-5777-474a-a13d-0693c7b74db3.png)
![SM Political Analysis - 4 (11)](https://user-images.githubusercontent.com/65197541/131225643-0ff23457-eada-4b2a-98d0-256e8ecd5df7.png)
![SM Political Analysis - 4 (12)](https://user-images.githubusercontent.com/65197541/131225654-089ce37f-7f7d-42b9-8972-5dba199252f8.png)
