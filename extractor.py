import re
from bs4 import BeautifulSoup


def style_remover(text):
    result1 = re.finditer(r"<style", text)
    result2 = re.finditer(r"</style>", text)

    styles = []
    for m, n in zip(result1, result2):
        style = text[m.start() : n.end()]
        styles.append(style)

    for style in styles:
        text = text.replace(style, "")
    return text


def get_div():

    with open("index.html") as file:
        text = file.read()

    # find main div
    result = re.search(r'<div id="zeus-root">', text)
    start = result.start()
    for match in re.finditer(r"</div*>", text):
        end = match.end()

    # clean style tags
    text = text[start:end]
    text = style_remover(text)

    with open("new-index.html", "w") as file:
        file.write(text)


def get_products(response_text):
    soup = BeautifulSoup(response_text, "html.parser")
    results = soup.select_one("div[data-testid*=ContentProducts]").select(
        "div[data-testid=master-product-card]"
    )
    products = []
    for p in results:

        # get product details
        title = p.select_one("div[data-testid=spnSRPProdName]").text
        image = p.select_one("img").get("src")
        link = p.select_one("a").get("href")
        price = p.select_one("div[data-testid=spnSRPProdPrice]").text
        prev_price = p.select_one("div[data-testid=lblProductSlashPrice]")
        if prev_price:
            prev_price = prev_price.text
        disc = p.select_one("div[data-testid=spnSRPProdDisc]")
        if disc:
            disc = disc.text
        else:
            disc = "0%"
        city = p.select_one("span[data-testid=spnSRPProdTabShopLoc]")
        seller = city.find_next("span").text
        seller_city = city.text
        ratings = p.select_one("span[class*=prd_rating]")
        if ratings:
            ratings = ratings.text
        solds = p.select_one("span[class*=prd_label-integrity]")
        if solds:
            solds = solds.text
        else:
            solds = "0 terjual"

        # construct product
        product = {
            "title": title,
            "image": image,
            "link": link,
            "price": price,
            "prev_price": prev_price,
            "disc": disc,
            "seller": seller,
            "seller_city": seller_city,
            "ratings": ratings,
            "solds": solds,
        }
        products.append(product)
    return products


def product_to_html(p):
    seller_path = p["link"].split("/")[3]
    html = f"""<div class="container">
        <img src="{p['image']}" alt="{p['title']}" />
        <div class="wrapper">
            <p class="title"><a href="{p['link']}">{p['title']}</a></p>
            <p>
                <a href="https://www.tokopedia.com/{seller_path}">{p['seller']},</a>
                <span>{p['seller_city']}</span>
            </p>
            <p>Harga <span>{p['price']}</span></p>
            <p>{p['solds']}</p>
        </div>
    </div>
    """
    return html
