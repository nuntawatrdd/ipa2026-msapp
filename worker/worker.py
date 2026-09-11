import os
import time
import json
import pika

from bson import json_util
from netmiko import ConnectHandler
from database import save_interface_status


def process_job(ch, method, properties, body):
    router_ip = None
    try:
        data = json_util.loads(body.decode('utf-8'))

        router_ip = data.get("ip")
        username = data.get("name")
        password = data.get("password")

        print(f"Received job for router {router_ip}")

        device = {
            'device_type': 'cisco_ios',
            'host': router_ip,
            'username': username,
            'password': password,
        }

        with ConnectHandler(**device) as net_connect:
            interfaces = net_connect.send_command(
                'show ip interface brief', use_textfsm=True
            )

        print(json.dumps(interfaces, indent=2))

        save_interface_status(router_ip, interfaces)
        print(f"Stored interface status for {router_ip}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Failed processing job for {router_ip}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    user = os.environ.get("RABBITMQ_USER", "admin")
    password = os.environ.get("RABBITMQ_PASS", "rabbitmq")

    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host, credentials=credentials
    )

    retry = 0
    while True:
        print(f"Connecting to RabbitMQ (try {retry})...")
        try:
            connection = pika.BlockingConnection(parameters)
            break
        except Exception as e:
            print(f"Failed: {e}")
            retry += 1
            time.sleep(5)

    channel = connection.channel()
    channel.exchange_declare(exchange="jobs", exchange_type="direct")
    channel.queue_declare(queue="router_jobs")
    channel.queue_bind(
        queue="router_jobs",
        exchange="jobs",
        routing_key="check_interfaces",
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="router_jobs", on_message_callback=process_job
    )
    channel.start_consuming()


if __name__ == "__main__":
    main()
