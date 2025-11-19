import json
from io import BytesIO
from confluent_kafka import Consumer, KafkaException
from fastavro import reader, parse_schema

# Load Avro schema
def load_schema(schema_path):
    with open(schema_path, 'r') as f:
        return parse_schema(json.load(f))

# Deserialize Avro message
def deserialize_avro(avro_bytes, schema):
    bytes_io = BytesIO(avro_bytes)
    avro_reader = reader(bytes_io, schema)
    for record in avro_reader:
        return record

# Main consumer function
def run_consumer():
    # Kafka configuration
    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'order-consumer-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    }
    
    consumer = Consumer(config)
    consumer.subscribe(['orders'])
    schema = load_schema('../schemas/order.avsc')
    
    # Running average tracking
    total_price = 0.0
    count = 0
    
    print("Starting Kafka Consumer...")
    print("Listening for orders on 'orders' topic\n")
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                raise KafkaException(msg.error())
            
            # Deserialize message
            order = deserialize_avro(msg.value(), schema)
            
            # Update running average
            total_price += order['price']
            count += 1
            avg = total_price / count
            
            # Log order and updated average
            print(f"Received order: {order}")
            print(f"Running Average: ${avg:.2f} (Total: ${total_price:.2f}, Count: {count})\n")
    
    except KeyboardInterrupt:
        print("\nConsumer stopped by user")
    finally:
        consumer.close()

if __name__ == '__main__':
    run_consumer()
