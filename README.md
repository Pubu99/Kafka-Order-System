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
requirements.txt
README.md
```

## Prerequisites

- Python 3.9+ (virtual environment recommended)
- Local Kafka broker listening on `localhost:9092` (Confluent Platform, Apache Kafka, or Docker image)
- `orders` and `orders-dlq` topics (auto-created if the broker allows it)
- Windows PowerShell is assumed in the sample commands; adapt paths if you are on another OS

## Installation

```powershell
cd e:/ENGINEERING/FOE-UOR/SEM 8/Big Data Analysis/Assignment 1/Kafka-Order-System
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If `confluent_kafka` fails to build, install the [Confluent Kafka client prerequisites](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#quick-start) for your OS, then rerun `pip install -r requirements.txt`.

## Running the System

1. **Start Kafka (and ZooKeeper if required by your distribution).** Example for Apache Kafka:

   ```powershell
   .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
   .\bin\windows\kafka-server-start.bat .\config\server.properties
   ```

2. **Launch the consumer** so you can monitor the running average and DLQ behavior:

   ```powershell
   python kafka_project/consumer/consumer.py
   ```

3. **Send orders with the producer** in a separate shell:

   ```powershell
   python kafka_project/producer/producer.py
   ```

4. **Inspect the DLQ topic** if any messages fail all retries (optional):
   ```powershell
   kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic orders-dlq --from-beginning
   ```

## What to Expect

- Producer logs `Sent order: {...}` along with Kafka delivery confirmations.
- Consumer prints each order, whether processing succeeded, and the updated running average.
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
