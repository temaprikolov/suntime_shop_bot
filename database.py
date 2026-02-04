from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

os.makedirs('data', exist_ok=True)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    joined_at = Column(DateTime, default=datetime.now)
    is_admin = Column(Boolean, default=False)

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    item_name = Column(String(50), default='')
    item_text = Column(Text, default='')
    updated_at = Column(DateTime, default=datetime.now)

engine = create_engine('sqlite:///data/database.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def init_db():
    """Инициализация базы данных с начальными значениями"""
    session = Session()
    
    from config import config
    
    items = [
        (7, '🔥 РАСПРОДАЖА', config.ITEM_SALE_TEXT),
        (8, '🎲 РАНДОМНЫЙ ТОВАР', config.ITEM_RANDOM_TEXT),
        (1, 'НАЛИЧИЕ ЖИДКОСТЕЙ', config.ITEM1_TEXT),
        (2, 'НАЛИЧИЕ СН*СА И ПЛАСТИНОК', config.ITEM2_TEXT),
        (3, 'НАЛИЧИЕ ОДНОРАЗОВЫХ ОЭС', config.ITEM3_TEXT),
        (4, 'НАЛИЧИЕ РАСХОДНИКОВ', config.ITEM4_TEXT),
        (5, 'НАЛИЧИЕ POD-УСТРОЙСТВ', config.ITEM5_TEXT),
        (6, 'ИНФОРМАЦИЯ О ЗАВОЗЕ', config.INFO_TEXT)
    ]
    
    for item_id, name, text in items:
        product = session.query(Product).filter_by(id=item_id).first()
        if not product:
            product = Product(id=item_id, item_name=name, item_text=text)
            session.add(product)
            print(f"➕ Добавлен товар {item_id}: {name}")
        else:
            if not product.item_text or product.item_text != text:
                product.item_text = text
                product.item_name = name
    
    session.commit()
    session.close()
    print("✅ База данных проверена (8 товаров)")
