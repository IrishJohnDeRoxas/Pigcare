from bs4 import BeautifulSoup
import requests
import mysql.connector


urls = ['https://www.swineweb.com/', 'https://www.thepigsite.com/']

mydb = mysql.connector.connect(
    host="localhost",
    user='root',
    passwd='Biboy_321',
    database='pigcare2'
)
my_cursor = mydb.cursor()


my_cursor.execute('SELECT COUNT(*) FROM scraped_news;')
value = my_cursor.fetchone()[0]
mydb.commit()


def article_scrape(url):
    desc_format = url.css.select_one(
        'div.td-excerpt').text.strip().replace('\r\n\r\n\r\n\r\n', '')
    remove_read_more = desc_format.replace('Read more', '').strip()
    desc_split = remove_read_more.split()
    link = url.css.select_one('div.td-read-more a')
    img = url.css.select_one('img.entry-thumb')

    title = url.css.select_one('h3.entry-title').text
    date = url.find('time').text
    desc = ' '.join(desc_split[:9]) + '...'
    a = link.get('href')
    img_url = img.get('data-img-url')
    values = [title, date, desc, a, img_url, counter]
    return values


def news_scrape(url):
    link = url.css.select_one('div.article-summary-title a')
    date_text = url.css.select_one('span.align-items-center').text.strip()
    format_date = date_text.split()

    title = url.css.select_one('div.article-summary-title').text.strip()
    date = format_date[1] + ' ' + format_date[0] + ", " + format_date[2]
    desc = url.css.select_one('div.article-summary-text').text.strip() + '...'
    img_url = url.css.select_one('a.article-summary-image img').get('src')
    a = link.get('href')
    values = [title, date, desc, a, img_url, counter]

    return values


for url in urls:
    response = requests.get(url)
    doc = BeautifulSoup(response.content, 'html.parser')

    # Updates the scraped articles
    if value:

        if url == urls[0]:
            articles = doc.css.select('div.td_module_14 ')
            counter = 1
            for article in articles:

                query = 'UPDATE scraped_news SET  title = %s , date = %s, `desc` = %s, a = %s, img_url= %s WHERE `id` = %s '

                my_cursor.execute(query, article_scrape(article))
                mydb.commit()

                if counter == 3:
                    break
                else:
                    counter += 1

        # Updates the scraped news
        if url == urls[1]:
            latest_news_container = doc.css.select('section.content-block')[2]
            news_divs = latest_news_container.css.select('div.col-md-12')
            counter = 4
            for news in news_divs:

                query = 'UPDATE scraped_news SET  title = %s , date = %s, `desc` = %s, a = %s, img_url= %s WHERE `id` = %s '
                my_cursor.execute(query, news_scrape(news))
                mydb.commit()
                if counter == 6:
                    break
                else:
                    counter += 1

    # Scrape for the first time the urls
    else:

        # This the first URL getting scrape(Article first scrape)
        if url == urls[0]:
            articles = doc.css.select('div.td_module_14 ')

            counter = 1
            for article in articles:

                query = """
                        INSERT INTO scraped_news (`type`, title, date, `desc`, a, img_url) 
                        VALUES ("article", %s, %s, %s, %s, %s)
                        """
                values = article_scrape(article)[:-1]
                my_cursor.execute(query, values)
                mydb.commit()

                if counter == 3:
                    break
                else:
                    counter += 1

        # This the second URL getting scrape(News first scrape)
        if url == urls[1]:
            latest_news_container = doc.css.select('section.content-block')[2]
            articles = latest_news_container.css.select('div.col-md-12')

            counter = 1
            for article in articles:

                query = """
                        INSERT INTO scraped_news (`type`, title, date, `desc`, a, img_url) 
                        VALUES ("news", %s, %s, %s, %s, %s)
                        """
                values = news_scrape(article)[:-1]

                my_cursor.execute(query, values)
                mydb.commit()
                if counter == 3:
                    break
                else:
                    counter += 1

my_cursor.close()
mydb.close()
