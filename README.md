# Social Media Political Analysis
### Springboard Open-ended Capstone Project

## Objectives
### Problems & Questions
_How can we better develop educational materials to meet kids where they are?_
- is it worth it to spend money to advertise to youth for political campaigns - are they engaging with current events?
- what are kids talking about & why? What does our education system tell them and not tell them

### Goals
- understanding how age/youth impacts political indoctrination
- understanding social impacts of political events
- to understand colloquial knowledge of political concepts

### Overview:
- Use NewsAPI to find top news by day
- Parse news story title & article into individual words/phrases
- Count most important individual words & phrases
- Use top 3 most important words & phrases to search TikTok & Twitter
- Count number of tweets & TikToks mentioning key words & phrases

## Installation & Use
`sm_config.ini` should have the following layout and info:

  ```
  [PostgreSQLdb]
  host = <hostname>
  database = <db name>
  user = <db username>
  password = <db password>
  
[newsAuth]
  api_key = <NewsAPI.org API key>
  
[tiktokAuth]
  api_key = <tiktok API key>
  
[twitterAuth]
  api_key = <twitter API key>
  ```

Find more information about .ini configuration files in Python documentation: https://docs.python.org/3/library/configparser.html

