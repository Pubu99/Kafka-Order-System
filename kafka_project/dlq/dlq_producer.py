import json
from io import BytesIO
from confluent_kafka import Producer
from fastavro import writer, parse_schema

# Load Avro schema
def load_schema(schema_path):
    with open(schema_path, 'r') as f:
        return parse_schema(json.load(f))

# Serialize order to Avro format
def serialize_avro(order, schema):
    bytes_io = BytesIO()
    writer(bytes_io, schema, [order])
    return bytes_io.getvalue()

# Send failed order to DLQ
def send_to_dlq(order, producer, schema):
    avro_data = serialize_avro(order, schema)
    producer.produce(
        topic='orders-dlq',
        value=avro_data
    )
    producer.flush()
    print(f"  → Moved to DLQ: orderId {order['orderId']}")
