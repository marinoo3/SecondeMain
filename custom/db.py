from sqlalchemy import URL, MetaData, Table, create_engine, select, update, delete
from sqlalchemy.orm import sessionmaker

import os




class Database():

    def __init__(self) -> None:

        self.engine = self.__init_engine()
        self.conn = self.engine.connect()
        self.products_table = self.__init_products_table()
        self.session = sessionmaker(bind=self.engine)

    def __init_engine(self):

        connection_string = URL.create(
            'postgresql',
            username = os.environ['DATABASE_USERNAME'],
            password = os.environ['DATABASE_PASSWORD'],
            host = 'ep-lively-voice-a4jlzfbr.us-east-1.pg.koyeb.app',
            database = 'koyebdb'
        )

        engine = create_engine(connection_string, pool_recycle=150)

        return engine
    
    def __init_products_table(self):

        metadata = MetaData()
        products = Table('products', metadata, autoload_with=self.engine, extend_existing=True)
        
        return products
    
    def get_products(self, location:str):

        with self.session() as session:

            try:
                query = select(self.products_table).where(self.products_table.c.location == location)
                result = session.execute(query).fetchall()
            except Exception as e:
                raise Exception(f'Database error {e}')
            
        # format result as a list of dict (json) -> self.products
        products = []
        for row in result:
            p = { column.name: getattr(row, column.name) for column in self.products_table.columns }
            products.append(p)

        return products
    
    def add_product(self, product_attrs):

        with self.session() as session:

            try:
                query = self.products_table.insert().values(product_attrs).returning(self.products_table.c.id)
                result = session.execute(query)
                session.commit()

            except Exception as e:
                session.rollback()
                raise Exception(f'Database error {e}')
        
        new_product_id = result.fetchone()[0] if result.rowcount else None
        return new_product_id
    
    def move_product(self, product_id, new_values):

        with self.session() as session:

            try:

                query = update(self.products_table).where(self.products_table.c.id == product_id).values(new_values)
                result = session.execute(query)
                session.commit()

                if result.rowcount == 0:
                    raise Exception(f"No product found with ID {product_id}")
                
            except Exception as e:

                session.rollback()
                raise Exception(f'Database error {e}')
            
    
    def remove_product(self, product_id):

        with self.session() as session:

            try:

                query = delete(self.products_table).where(self.products_table.c.id == product_id)
                result = session.execute(query)
                session.commit()

                if result.rowcount == 0:
                    raise Exception(f"No product found with ID {product_id}")
                else:
                    print(f"Deleted {result.rowcount} row(s).")
                
            except Exception as e:

                session.rollback()
                raise Exception(f'Database error {e}')