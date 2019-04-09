import scrapy
import csv

#https://hsreplay.net/analytics/query/list_decks_by_win_rate/?GameType=RANKED_STANDARD&RankRange=ALL&Region=ALL&TimeRange=LAST_30_DAYS
class HSSpider(scrapy.Spider):
    name = "hs-wild"
    page1 = "https://www.hearthstonetopdecks.com/cards/?st=&manaCost=&format=wild&rarity=&type=&class=&set=&mechanic=&race=&orderby=ASC-name&view=table"
    baseUrl = "https://www.hearthstonetopdecks.com/cards/page/{0}/?st&manaCost&format=wild&rarity&type&class&set&mechanic&race&orderby=ASC-name&view=table"
    start_urls = [page1 if i == 0 else baseUrl.format(i+1) for i in range(0, 42)] #42

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'cards-wild.csv'
        cardList = response.css('#card-list > tr')
        results = []
        columns = [
            ("name", lambda tds: " ".join(tds[0].css('strong')[0].xpath('.//text()').getall())),
            ("text", lambda tds: " ".join(tds[0].css('small')[0].xpath('.//text()').getall())),
            ("class", lambda tds: tds[1].css('a::text').get()),
            ("rarity", lambda tds: tds[2].css('a::text').get()),
            ("type", lambda tds: tds[3].css('a::text').get()),
            ("cost", lambda tds: tds[4].xpath("./text()").get()),
            ("attack", lambda tds: tds[5].xpath("./text()").get()),
            ("health", lambda tds: tds[6].xpath("./text()").get()),
            ("durability", lambda tds: tds[7].xpath("./text()").get() if len(tds) >7 else None),
            ("image", lambda tds: tds[0].css('a').attrib['data-tooltip-img'])
        ]
        for sel in cardList:
            r = []
            tds = sel.css('td')
            results.append(
                map(
                    lambda y: "" if y == None else y.encode("utf-8"),
                    [c[1](tds) for c in columns]
                )
            )

        with open(filename, 'ab') as f: #append
            writer = csv.writer(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
            writer.writerows(results)
        self.log('Saved file %s' % filename)
