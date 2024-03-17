import pika
import ast
import time
import logging
import psycopg2

DATABASE_URI="postgresql://order_db_username:order_db_password@0.0.0.0:5432/order_db_dev"


def update_state(order_id, status):
    try:
        connection = psycopg2.connect(dbname="order_db_dev",
                                      user="order_db_username",
                                      password="order_db_password",
                                      host="order_db",
                                      port="5432")
        cursor = connection.cursor()
        time.sleep(10)
        query = f"update orders set status='{status}' where order_id='{order_id}'"
        cursor.execute(query)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        logging.info("Error while fetching data from PostgreSQL %s", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            logging.info("PostgreSQL connection is closed")


def callback(channel, method, properties, body):
    logging.info(f"[x] Received {body}")
    body_dict = ast.literal_eval(body.decode("UTF-8"))
    id, status = body_dict["order_id"], body_dict["status"]
    update_state(id, status)


credentials = pika.PlainCredentials('admin', 'food')
parameters = pika.ConnectionParameters('rabbitmq',
                                    5672,
                                    '/',
                                    credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='events')
channel.basic_consume(queue='events',
                    auto_ack=True,
                    on_message_callback=callback)
logging.info(' [*] Waiting for messages. To exit press CTRL+C')

if __name__ == "__main__":
    channel.start_consuming()
