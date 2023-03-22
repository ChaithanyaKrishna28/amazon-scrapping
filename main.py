import requests
from bs4 import BeautifulSoup
import csv

# File to save all products with basic info
file1 = open('item_1.csv', 'w', encoding='utf-8', newline='')
csvwriter1 = csv.writer(file1)
csvwriter1.writerow(['Product URL', 'Product Name', 'Price', 'Rating', 'Reviews'])

# File to save product manufacturer ASIN and Description
file2 = open('item_2.csv', 'w', encoding='utf-8', newline='')
csvwriter2 = csv.writer(file2)
csvwriter2.writerow(['Manufacturer', 'ASIN', 'Description'])


def scrape(html):
    # find all div which shows result
    maindiv = html.find_all('div', attrs={"data-component-type": "s-search-result"})

    # Retrieve info for each item
    for i in maindiv:
        head = i.find('h2')
        ProductName = head.find('span').string
        url = "https://www.amazon.in"+head.find('a')['href']

        # Some promotional products dont contain Price value
        try:
            price = i.find('span', attrs={"class": "a-offscreen"}).string.strip('\"')
        except:
            continue
        # Some products dont contain rating
        # Wcich requires us to use try and except
        try:
            rating = i.find('span', attrs={"class": "a-icon-alt"}).string.split(' ')
            reviews = i.find('span', attrs={"class": ["a-size-base s-underline-text"]}).string.strip('\"')[1:-1]
        except:
            rating = ['0']
            reviews = '0'

        data = [url, ProductName, price[1:], rating[0], reviews]

        # write into csv file
        csvwriter1.writerow(data)


def ProductDetails(Product):
    data = []
    Manufacturer = ''
    ASIN = ''
    Productinfo = Product.find(id="detailBullets_feature_div")
    try:
        listitems = Productinfo.find_all('li')
        for item in listitems:
            if item is not None:
                key = item.find('span', attrs={"class": "a-text-bold"})
                if key is not None:
                    if key.string.startswith('Manufacturer'):
                        spans = item.find_all('span')
                        Manufacturer = spans[2].string
                    if key.string.startswith('ASIN'):
                        spans = item.find_all('span')
                        ASIN = spans[2].string
    except:
        table = Product.find(id="productDetails_detailBullets_sections1")
        rows = table.find_all('tr')
        for row in rows:
            if row is  not None:
                if row.find('th').string.strip() == 'ASIN':
                    ASIN = row.find('td').string.strip()
                if row.find('th').string.strip() == 'Manufacturer':
                    Manufacturer = row.find('td').string.strip()
        table2 = Product.find(id="productDetails_techSpec_section_1")
        rows = table2.find_all('tr')
        for row in rows:
            if row is not None:
                if row.find('th').string.strip() == 'ASIN':
                    ASIN = row.find('td').string.strip()
                    print(ASIN)
                if row.find('th').string.strip() == 'Manufacturer':
                    Manufacturer = row.find('td').string.strip()

    para = []
    description1 = Product.find(id='aplus')
    description2 = Product.find(id='productDescription_feature_div')
    try:
        para += description1.find_all('p')
    except:
        pass
    try:
        para += description2.find_all('p')
    except:
        pass
    Description = ''
    # Find all Description
    for i in para:
        if i.string:
            Description += ' ' + i.string

    # write data into File
    csvwriter2.writerow([(Manufacturer.encode('ascii', 'ignore')).decode(), ASIN, Description.strip()])


def main():
    # requestheader copied from my browser
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9'
    }
    # search url
    #URL = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

    # #Scrape 20 webpage search results
    for i in range(1, 21):
        responses = requests.get( url = f"https://www.amazon.in/s?k=bags&page={i}&crid=2M096C61O4MLT&qid=1679410486&sprefix=ba%2Caps%2C358&ref=sr_pg_{i}",headers=header, stream=True)
        #responses = requests.get(URL + str(i), headers=header, stream=True)  # Append i to go to another search page
        if responses.status_code == 200:  # check if response is good
            html = BeautifulSoup(responses.text, "html.parser")
            scrape(html)  # Scrape through that webpage

        else:
            #print("Unable to reach site", URL + str(i))
            print("Unable to reach site",f"https://www.amazon.in/s?k=bags&page={i}&crid=2M096C61O4MLT&qid=1679410486&sprefix=ba%2Caps%2C358&ref=sr_pg_{i}" )
    file1.close()

    # find detailed info of products
    fil = open('item_1.csv', 'r', encoding='utf-8')
    products = csv.reader(fil)
    next(products, None)  # skip the headers
    for row in products:

        ProductURL = row[0]

        responses = requests.get(ProductURL, headers=header, stream=True)
        print(ProductURL)
        if responses.status_code == 200:  # check if response is good
            product = BeautifulSoup(responses.text, "html.parser")
            ProductDetails(product)  # Scrape through that webpage

        else:
            print("Unable to reach site", ProductURL)
    file2.close()


if __name__ == "__main__":
    main()