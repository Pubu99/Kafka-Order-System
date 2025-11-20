# Kafka Order System

Minimal Kafka + Avro assignment that streams randomized orders, aggregates their running average in real time, retries transient failures, and forwards unrecoverable payloads to a Dead Letter Queue (DLQ). The project favors plain Python functions and a tiny folder structure so it stays easy to explain in a live demo.

## Features

- **Avro schema** (`schemas/order.avsc`) shared by producer, consumer, and DLQ sender
- **Order producer** generates lightweight random payloads and pushes them to the `orders` topic
- **Consumer with aggregation** keeps `total_price`, `count`, and `avg` metrics per message
- **Retry logic** simulates temporary processing failures (max 3 attempts) before declaring a permanent error
- **Dead Letter Queue** forwards failed payloads to `orders-dlq` and logs `Moved to DLQ: orderId X`

## Repository Layout

```
kafka_project/
├── producer/
│   └── producer.py
├── consumer/
│   └── consumer.py
├── dlq/
│   └── dlq_producer.py
└── schemas/
    └── order.avsc
docker-compose.yml      # Kafka + ZooKeeper setup
Dockerfile              # Python app container (optional)
.dockerignore
requirements.txt
README.md
```

## Prerequisites

### Option 1: Docker (Recommended)

- Docker Desktop installed and running
- Docker Compose

### Option 2: Local Setup

- Python 3.9+ (virtual environment recommended)
- Local Kafka broker listening on `localhost:9092` (Confluent Platform or Apache Kafka)
- `orders` and `orders-dlq` topics (auto-created if the broker allows it)
- Windows PowerShell is assumed in the sample commands; adapt paths if you are on another OS

## Installation & Running

### Option 1: Using Docker (Easiest)

1. **Start Kafka and ZooKeeper with Docker Compose:**

   ```powershell
   docker-compose up -d
   ```

   This starts Kafka on `localhost:9092` and ZooKeeper on `localhost:2181`.

2. **Verify services are running:**

   ```powershell
   docker-compose ps
   ```

   Both `zookeeper` and `kafka` should show as "Up".

3. **Install Python dependencies locally** (for running producer/consumer on your host):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Run the consumer:**

   ```powershell
   python kafka_project/consumer/consumer.py
   ```

5. **Run the producer** (in a separate terminal):

   ```powershell
   python kafka_project/producer/producer.py
   ```

6. **Stop Docker services when done:**
   ```powershell
   docker-compose down
   ```

### Option 2: Local Kafka Setup

1. **Install Python dependencies:**

   ```powershell
   cd e:/ENGINEERING/FOE-UOR/SEM 8/Big Data Analysis/Assignment 1/Kafka-Order-System
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Start Kafka and ZooKeeper manually:**

   ```powershell
   # Terminal 1: Start ZooKeeper
   cd C:\kafka
   .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties

   # Terminal 2: Start Kafka
   cd C:\kafka
   .\bin\windows\kafka-server-start.bat .\config\server.properties
   ```

3. **Create topics:**

   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-topics.bat --create --topic orders --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   .\bin\windows\kafka-topics.bat --create --topic orders-dlq --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   ```

4. **Run the consumer:**

   ```powershell
   python kafka_project/consumer/consumer.py
   ```

5. **Run the producer** (in a separate terminal):
   ```powershell
   python kafka_project/producer/producer.py
   ```

## Inspecting the DLQ

To view messages in the Dead Letter Queue:

**With Docker:**

```powershell
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders-dlq --from-beginning
```

**With Local Kafka:**

```powershell
cd C:\kafka
.\bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic orders-dlq --from-beginning
```

## What to Expect

**Producer Output:**

```
Starting Kafka Producer...
Sending orders to 'orders' topic

Sent order: {'orderId': 'ORD-6882', 'product': 'Headphones', 'price': 294.48}
Message delivered to orders [0]
Sent order: {'orderId': 'ORD-7474', 'product': 'Tablet', 'price': 995.01}
Message delivered to orders [0]
...
```

**Consumer Output:**

- Each order is received and deserialized
- Processing succeeds (✓) or retries up to 3 times
- Running average is calculated and displayed
- Failed messages after 3 retries are sent to DLQ

Example:

```
Starting Kafka Consumer...
Listening for orders on 'orders' topic

Received order: {'orderId': 'ORD-6882', 'product': 'Headphones', 'price': 294.48}
✓ Processing successful
Running Average: $294.48 (Total: $294.48, Count: 1)

Received order: {'orderId': 'ORD-7474', 'product': 'Tablet', 'price': 995.01}
  Attempt 1/3 failed: Temporary processing failure
  Attempt 2/3 failed: Temporary processing failure
✓ Processing successful
Running Average: $644.75 (Total: $1289.49, Count: 2)
```

- When simulated retries fail three times, the consumer prints `Permanent failure` and `Moved to DLQ: orderId X`.
- The DLQ topic receives the Avro-serialized payload exactly as the original producer emitted it.

## Demonstration Tips

- Keep the consumer window visible to highlight the running average math (`total_price`, `count`, `avg`).
- Mention that retry timing and failure likelihood (`30%`) are configurable inside `consumer.py`.
- Show the DLQ consumer after forcing a few failures so stakeholders can see resiliency in action.

## Troubleshooting

- **`confluent_kafka` import errors**: Verify the package installed inside your active virtual environment and that `librdkafka` dependencies are present.
- **No messages consumed**: Confirm `orders` exists and the producer uses the same broker URL as the consumer.
- **DLQ stays empty**: Reduce the random threshold in `process_order` to increase simulated failures while testing.
