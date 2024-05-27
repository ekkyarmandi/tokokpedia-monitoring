import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config

from extractor import get_products, product_to_html


def main():
    url = config("SEARCH_URL")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }

    res = requests.get(url, headers=headers)
    products = get_products(res.text)

    # exclude keywords
    exclude = config("EXCLUDE_KEYWORDS").split(",")
    products = list(
        filter(
            lambda p: all(keyword not in p["title"].lower() for keyword in exclude),
            products,
        )
    )

    # exclude urls
    blacklist = config("BLACKLIST_URLS").split(",")
    products = list(filter(lambda p: p["link"] not in blacklist, products))

    # construct product html
    container = "<div>{}</div>"
    container = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html lang="id" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Tokkped Monitoring</title>
        <style>
        .container {
            font-family: Arial, Helvetica, sans-serif;
            display: flex;
            padding: 8px;
        }
        .wrapper {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .title {
            font-size: 1.5rem;
            font-weight: bold;
        }
        img {
            border: 1px solid #ddd;
            overflow: hidden;
            margin-right: 10px;
        }
        </style>
    </head>
    <body>{}</body>
    </html>
    """
    body = "\n".join([product_to_html(p) for p in products])

    sender = "ekkyarmandi@gmail.com"
    receiver = "ekkyarmandi@gmail.com"
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        # login
        smtp.login(sender, config("EMAIL_KEY"))
        # construct the message
        msg = MIMEMultipart()
        msg["subject"] = "Today Tokopedia Search Result for 'Cidoo 65'"
        msg.attach(MIMEText(body, "html", "utf-8"))
        # send the email
        smtp.sendmail(sender, receiver, msg.as_string())


if __name__ == "__main__":
    main()
