import psycopg2, requests, os, shutil
from bs4 import BeautifulSoup

dbname = os.getenv("dbname")
user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")

try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
except:
    print('Can`t establish connection to database')
    exit()


if __name__ == "__main__":
    
    # del all pics from news
    try:
        shutil.rmtree("/home/gitlab-runner/bdsec/static/img/news/")
    except:
        pass
    os.mkdir("/home/gitlab-runner/bdsec/static/img/news/")

    url = 'https://securitymedia.org/news'
    domain = 'https://securitymedia.org'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    imgs = soup.find_all("img", class_="img-fluid")[:3]
    headers = soup.find_all("div", class_="h4")[:3]
    bodies = soup.find_all("div", class_="col-md-8")[:3]

    for i in imgs:
        lnk = domain + i["src"]
        with open("/home/gitlab-runner/bdsec/static/img/news/" + str(lnk).split("/")[-1], "wb") as f:
            f.write(requests.get(lnk).content)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM news")

    for i in range(len(imgs)):
        header = headers[i].text
        
        body = bodies[i]
        body.div.decompose()
        body.div.decompose()
        body = body.text.replace("\n", "").replace("\r", "").replace("\t", "").strip()

        img = imgs[i]["src"].split("/")[-1]

        cursor.execute("INSERT INTO news (header, body, img) VALUES (%s, %s, %s)".format(header, body, img))

    cursor.close()
    conn.close()
