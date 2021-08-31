"""Proxies"""
# rotate proxies
# url = "http://icanhazip.com"
# proxy_host = "proxy.crawlera.com"
# proxy_port = "8010"
# proxy_auth = "<APIKEY>:" # API key from crawlera to prevent request rejection
# proxies = {
#     "https": f"https://{proxy_auth}@{proxy_host}:{proxy_port}/",
#     "http": f"http://{proxy_auth}@{proxy_host}:{proxy_port}/"
# }

   # def get_free_proxies(self):
#     url = "https://free-proxy-list.net/"
#     # get the HTTP response and construct soup object
#     bs = BeautifulSoup()
#     soup = bs(requests.get(url).content, "html.parser")
#     proxies = []
#     for row in soup.find_all("table", attrs={"id": "proxylisttable"})[0].find("tr")[1:]:
#         tds = row.find_all("td")
#         try:
#             ip = tds[0].text.strip()
#             port = tds[1].text.strip()
#             host = f"{ip}:{port}"
#             proxies.append(host)
#         except IndexError:
#             continue
#     return proxies

      # use proxies to prevent request rejection
#self.proxies = {"http": "http://10.10.10.10:8000",
# "https": "https://10.10.10.10:8000"
# }
