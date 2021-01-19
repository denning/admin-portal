from django.core.management.base import BaseCommand
from django.db import connection
from apps.greencheck.legacy_workers import LegacySiteCheckLogger
import pika
import logging

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
logger.addHandler(console)
logger.setLevel(logging.WARN)

class Command(BaseCommand):
    help = "Start a worker consuming from legacy app queue"

    def handle(self, *args, **options):

        sitecheck_logger = LegacySiteCheckLogger()

        def on_message(channel, method_frame, header_frame, body):
            logger.debug(f"message received for {channel}")
            logger.debug(method_frame)
            logger.debug(body)
            logger.debug(method_frame.delivery_tag)
            # import ipdb ; ipdb.set_trace()

            sitecheck_logger.parse_and_log_to_database(body)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        parameters = pika.URLParameters('amqp://greencheck_worker:consult-pottage-pamper-managua-pemmican@localhost:5672/')

        mq_connection = pika.BlockingConnection(parameters)
        channel = mq_connection.channel()
        channel.basic_consume('enqueue.app.default', on_message)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        except Exception as error:
            logger.exception(error)
            import ipdb ; ipdb.set_trace()
            channel.stop_consuming()

        mq_connection.close()


