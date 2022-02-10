from ceneo_scraper import CeneoScraper

scraper = CeneoScraper()


def load_products():
    scraper.data_load()


def scrape_products_prices():
    all_products = scraper.get_all_products()
    for product in all_products:
        response = scraper.request_ceneo_product_page(product.Ceneo_Id)
        product_lowest_price = scraper.find_product_lowest_price(response)
        scraper.add_product_price(ceneo_id=product.Ceneo_Id, product_price=product_lowest_price)
        scraper.price_alert_verification(product_name=product.Product_Name, lowest_price=product_lowest_price, alert_price=product.Alert_Price)


def run():
    all_products = scraper.get_all_products()
    if all_products:
        scrape_products_prices()
    else:
        load_products()
        scrape_products_prices()


if __name__=="__main__":
    run()
