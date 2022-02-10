from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Float, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists
from datetime import datetime
import json

Base = declarative_base()


class Products(Base):
    __tablename__ = 'Products'

    Id = Column(Integer, primary_key=True)
    Product_Name = Column(String, nullable=False)
    Ceneo_Id = Column(String, nullable=False, unique=True)
    Alert_Price = Column(Float, nullable=False)
    productdata = relationship('ProductData', back_populates='products', cascade='all, delete, delete-orphan')

class ProductData(Base):
    __tablename__ = 'Products_Data'

    Id = Column(Integer, primary_key=True, nullable=False)
    Product_Ceneo_Id = Column(Integer, ForeignKey('Products.Ceneo_Id'), nullable=False)
    Product_Price = Column(Float, nullable=False)
    Timestamp = Column(String)

    products = relationship('Products')


class ScraperDB(Products):

    database = 'sqlite:///products.db'

    def __init__(self):
        self.now = datetime.now()
        if not database_exists(self.database):
            try:
                self.db = create_engine(self.database, echo=False)
                Base.metadata.create_all(self.db)
            except Exception as e:
                print(e)
        try:
            self.db = create_engine(self.database, echo=False)
        except Exception as e:
            print(e)
        db_session = sessionmaker(bind=self.db)
        self.session = db_session()

    def add_product(self, product_name: str, ceneo_id: str, alert_price: str):
        """
        Add single product to database. Required product name: str, ceneo id: str, target price: float.
        If database does not exist then will be created.
        """
        product = Products(Product_Name=product_name, Ceneo_Id=ceneo_id, Alert_Price=alert_price)
        try:
            self.session.add(product)
        except Exception as e:
            print(e)
            self.session.rollback()
        else:
            self.session.commit()
        print(f'Product: {product.Product_Name} was added to database.')

    def add_product_price(self, ceneo_id: str, product_price: str):
        """
        Adds product price into table Products_Data with ate and time of the record.
        :param ceneo_id: Unique product ceneo id.
        :param product_price: Recorded product price.
        :return:
        """
        product_price = ProductData(Product_Ceneo_Id=ceneo_id, Product_Price=product_price, Timestamp=self.now.strftime("%d/%m/%Y %H:%M:%S"))
        try:
            self.session.add(product_price)
        except Exception as e:
            print(e)
            self.session.rollback()
        else:
            self.session.commit()

    def delete_product(self, ceneo_id: str):
        """
        Delete single from database with all recorded data.
        :param ceneo_id: Unique product ceneo id.
        :return:
        """
        product = self.session.query(Products).filter_by(Ceneo_Id=ceneo_id).first()
        try:
            self.session.delete(product)
        except Exception as e:
            print(e)
            self.session.rollback()
        else:
            self.session.commit()

        print(f'Product: {product.Product_Name} deleted.')

    def export_all_products(self):
        """
        Export all products (all data from table Products).
        Output in .csv file.
        """
        try:
            all_products = self.session.query(Products).all()
        except Exception as e:
            print(e)
        with open('Products.csv', 'w') as f:
            for product in all_products:
                f.write(f'{product.Id},{product.Product_Name},{product.Ceneo_Id},{product.Alert_Price}\n')
        print(f'{len(all_products)} products were exported.')

    def export_product_prices(self):
        """
        Exports all products daa in separate csv files. eg. file: ProductX.csv => product price, date & time when
        price was recorded.
        """
        try:
            product_prices = self.session.query(Products, ProductData).filter(Products.Ceneo_Id ==ProductData.Product_Ceneo_Id).all()
            for product in product_prices:
                with open(f'{product[0].Product_Name}.csv', 'a') as file:
                    file.write(f'{product[1].Product_Price},{product[1].Timestamp}\n')
        except Exception as e:
            print(e)

    def get_all_products(self):
        """
        Get all products from data base.
        :return: all_products -> list of objects
        """
        try:
            all_products = self.session.query(Products).all()
        except Exception as e:
            print(e)
        return all_products

    def data_load(self):
        """
        Loads data in database into a table Products from json file.
        If database: products.json exist with data loaded product will be additionally added
        previous product will not be removed). I
        """
        try:
            with open('products.json', 'r') as payload:
                data = json.load(payload)
                for product in data["products"]:
                    prod = Products(Product_Name=product['productName'], Ceneo_Id=product['ceneoId'], Alert_Price=product['targetPrice'])
                    self.session.add(prod)
        except Exception as e:
            print(e)
        self.session.commit()

        print(f'{len(data["products"])} products loaded.')