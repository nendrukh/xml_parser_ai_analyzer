import xml.etree.ElementTree as ET
import logging
import traceback
from datetime import datetime

from openai import OpenAI
from asgiref.sync import async_to_sync
import xmltodict

from celery_app import celery_app
from models import Product
from database import Database

logger = logging.getLogger()


def request_to_ai(prompt: str) -> str:
    """
    Делаем запрос к LLM OpenAI и на выходе получаем ответ от модели
    :param prompt: Промпт для LLM
    :return: Ответ модели
    """
    ai_client = OpenAI()

    if ai_client.api_key == "Api key...":
        logger.error("OpenAI API key not specified in .env file")
        raise Exception("OpenAI API key not specified in .env file")

    completion = ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional sales analyst."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return completion.choices[0].message.content


async def xml_processing(xml_str: str):
    """
    Парсим данные о продажах из xml, получаем аналитику от LLM и сохраняем ответ в базу
    :param xml_str: валидный xml с продажами в виде строки
    """
    products_elems: ET.Element = ET.fromstring(xml_str)
    date = products_elems.get("date")

    await Database.create_tables()
    await Database.execute_to_db(
        f"""INSERT INTO ai_analytics(sales_date, status) VALUES ($1, 'IN_PROGRESS')""",
        datetime.strptime(date, "%Y-%m-%d"))
    response_db = await Database.fetch_to_db("SELECT id FROM ai_analytics ORDER BY id DESC limit 1")
    analytics_id = response_db[0]["id"]

    try:
        total_revenue = 0
        all_products = {}

        for product in products_elems.find("products"):
            product = Product.model_validate(xmltodict.parse(ET.tostring(product))["product"])
            total_revenue += product.price * product.quantity
            all_products.setdefault(product.name, {"quantity": product.quantity, "category": product.category})
            all_products[product.name]["quantity"] += 1

            await Database.execute_to_db("""INSERT INTO sales_data(
            sales_date,
            product_id,
            product_name,
            quantity,
            price,
            category,
            ai_analytics_id)
            VALUES
            ($1, $2, $3, $4, $5, $6, $7)""",
                                         datetime.strptime(date, "%Y-%m-%d"),
                                         product.id,
                                         product.name,
                                         product.quantity,
                                         product.price,
                                         product.category,
                                         analytics_id)

        top_3 = sorted(all_products.items(), key=lambda item: item[1]["quantity"], reverse=True)[:3]
        top_products = [product[0] for product in top_3]
        categories = [product[1]["category"] for product in top_3]
        logger.info(f"date: {date}, top_products: {top_products}, categories: {categories}")

        prompt = f"""Проанализируй данные о продажах за {date}:
        1. Общая выручка: {total_revenue}
        2. Топ-3 товара по продажам: {top_products}
        3. Распределение по категориям: {categories}
    
        Составь краткий аналитический отчет с выводами и рекомендациями."""
        result = request_to_ai(prompt)
        await Database.execute_to_db("UPDATE ai_analytics SET prompt=$1, ai_answer=$2, status='FINISHED' where id=$3",
                                     prompt, result, analytics_id)

    except Exception as e:
        logger.error(traceback.format_exc())
        await Database.execute_to_db("UPDATE ai_analytics SET status='ERROR' where id=$1", analytics_id)
        raise Exception(e)

    return result


@celery_app.task
def executor(xml: str):
    return async_to_sync(xml_processing)(xml)
