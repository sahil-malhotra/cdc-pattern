import os
import psycopg2
import psycopg2.extras
import logging
import time
from kafka import KafkaProducer
import json
from dotenv import load_dotenv


class PostgresCDC:

    def __init__(self, host, port, dbname, user, password, replication_slot):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.replication_slot = replication_slot
        self.cur = None
        self.conn = None

    def start_replication_server(self):
        """Setup/Connect to the replication slots at Postgres
        """
        connect_string = 'host={0} port={1} dbname={2} user={3} password={4}'.format(
            self.host, self.port, self.dbname, self.user, self.password)
        self.conn = psycopg2.connect(
            connect_string, connection_factory=psycopg2.extras.LogicalReplicationConnection)
        self.cur = self.conn.cursor()
        try:
            self.cur.start_replication(
                slot_name=self.replication_slot, decode=True)
        except psycopg2.ProgrammingError:
            self.cur.create_replication_slot(
                self.replication_slot, output_plugin='wal2json')
            self.cur.start_replication(
                slot_name=self.replication_slot, decode=True)

    def start_streaming(self, stream_receiver):
        """Listen and consume streams
        Args:
            cur (object): Cursor object
            conn (object): Connection object
            stream_receiver (function): Function to execute received streams
        """
        while True:
            logging.info("Starting streaming, press Control-C to end...")
            try:
                self.cur.consume_stream(stream_receiver)

            except KeyboardInterrupt:
                self.cur.close()
                self.conn.close()
                logging.warning("The slot '{0}' still exists. Drop it with "
                                "SELECT pg_drop_replication_slot('{0}'); if no longer needed.".format(self.replication_slot))
                logging.info("Transaction logs will accumulate in pg_wal "
                             "until the slot is dropped.")
                return
            except:
                time.sleep(5)
                try:
                    self.start_replication_server()
                except Exception as e:
                    logging.error(e)


def send_to_destination(msg):
    logging.info("Stream msg: " + msg.payload)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    load_dotenv(verbose=True)
    cdc = PostgresCDC(
        os.getenv('POSTGRES_HOST'), os.getenv('POSTGRES_PORT'), os.getenv('POSTGRES_DBNAME'), os.getenv('POSTGRES_USER'), os.getenv('POSTGRES_PASSWORD'), os.getenv('POSTGRES_REPLICATION_SLOT'))
    cdc.start_replication_server()
    cdc.start_streaming(send_to_destination)
