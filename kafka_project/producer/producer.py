import json
import random
import time
from io import BytesIO
from confluent_kafka import Producer
from fastavro import writer, parse_schema

# Load Avro schema
def load_schema(schema_path):
    # Convert to absolute path relative to this script
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(script_dir, schema_path)
    with open(abs_path, 'r') as f:
        return parse_schema(json.load(f))

# Serialize order to Avro format
def serialize_avro(order, schema):
    bytes_io = BytesIO()
    writer(bytes_io, schema, [order])
    return bytes_io.getvalue()

# Generate random order
def generate_order():
    products = ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard', 'Mouse', 'Headphones']
    order = {
        'orderId': f'ORD-{random.randint(1000, 9999)}',
        'product': random.choice(products),
        'price': round(random.uniform(10.0, 1000.0), 2)
    }
    return order

# Kafka delivery callback
def delivery_callback(err, msg):
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

# Main producer function
def run_producer():
    # Kafka configuration
    config = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'order-producer'
    }
    
    producer = Producer(config)
    schema = load_schema('../schemas/order.avsc')
    
    print("Starting Kafka Producer...")
    print("Sending orders to 'orders' topic\n")
    
    try:
        for i in range(10):  # Send 10 orders
            order = generate_order()
            avro_data = serialize_avro(order, schema)
            
            # Send to Kafka
            producer.produce(
                topic='orders',
                value=avro_data,
                callback=delivery_callback
            )
            
            print(f"Sent order: {order}")
            producer.poll(0)
            time.sleep(1)  # Wait 1 second between orders
        
        # Wait for all messages to be delivered
        producer.flush()
        print("\nAll orders sent successfully!")
        
    except KeyboardInterrupt:
        print("\nProducer stopped by user")
    finally:
        producer.flush()

if __name__ == '__main__':
    run_producer()
