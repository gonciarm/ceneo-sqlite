import requests, re, gspread, smtplib
from database import ScraperDB
from datetime import date
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from e_mail import Email


class CeneoScraper(Email, ScraperDB):
    url = 'https://www.ceneo.pl/'

    def __init__(self):
        ScraperDB.__init__(self)

    def request_ceneo_product_page(self, ceno_product_id):
        """
        Get ceneo product webpage.
        :param ceno_product_id: id of product in ceneo
        :return: ceneo product page
        """
        with requests.Session() as s:
            response = s.get(self.url + str(ceno_product_id), verify=False)
        return response

    def find_product_lowest_price(self, response):
        """
        Search for product lowest price.
        :param response: ceneo product page
        :return: product lowest price
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        script_text = soup.find_all('script')
        text = str(script_text)
        lowest_price = float(re.search(r'"lowPrice":.+\d', text).group().split(' ')[1])
        return lowest_price

    def price_alert_email(self, product_name, lowest_price):
        """
        Send email with price alert.
        Configured with emial on gmail.com
        :param product_name: Product Name
        :param lowest_price: Product Lowest Price
        """
        msg = MIMEMultipart()
        msg['To'] = self.email_address
        msg['From'] = self.email_address
        msg['Subject'] = self.email_subject(product_name)
        msg.attach(MIMEText(self.email_body(product_name, lowest_price), 'plain'))
        email_text = msg.as_string()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # mail server configuration
        server.ehlo()
        server.login(self.email_address, self.email_app_pass)
        # send mail >> sent from, send to, email message
        server.sendmail(self.email_address, self.email_address, email_text)
        server.close()

    def price_alert_verification(self, product_name, lowest_price, alert_price):
        """
        If found product price (lowest price) reaches configured alert price triggers email alert.
        :param product_name: Product Name.
        :param lowest_price: Fount product lowest price.
        :param alert_price: Set product price that triggers price alert email.
        """
        if lowest_price <= alert_price:
            self.price_alert_email(product_name=product_name, lowest_price=lowest_price)

