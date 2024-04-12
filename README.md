# Distributed Load Testing System
# Goal
Design and build a distributed load-testing system that co-ordinates between
multiple driver nodes to run a highly concurrent, high-throughput load test on a
web server. This system will use Kafka as a communication service.
# Architecture
![image](https://github.com/samarth0104/Distributed-Load-Testing-System-main/assets/144517774/e2c9ef28-033e-4722-97e8-08c1f1972bdc)

The orchestrator node and driver node are implemented as separate processes
(you do not need to provision separate VMs for each)
The Orchestrator node and the Driver node must communicate via Kafka (see
topic and message descriptor)
The Orchestrator node and driver node must roughly have the above described
components.
Final Deliverables
Functionality
The system must use Kafka as a single point of communication, publishing and
subscribing roughly to the below topics. If you feel like there can be an
improvement in the format (within reasonable bounds) you are free to implement
it.

All nodes take the Kafka IP Address and the Orchestrator node IP Address as
command-line arguments.
All Nodes must possess a uniqe ID That they use to register themselves, and
be capable of generating unique IDs as necessary.
The system must support the two following types of load tests

Tsunami testing: The user must be able to set a delay interval between
each request, and the system must maintain this gap between each request on
each node
Avalanche testing: All requests are sent as soon as they are ready in
first-come first-serve order
The user must provide a target throughput per driver node (X requests per
second) and the implementation must respect that. The user must provide a
total number of requests to be run per driver node in the test
configuration. The test stops on each driver node once the responses to all
of these requests have been recieved.
If you have already implemented features for a target throughput, that
will be considered as well, and you will get marks for it.
There is no time bound for when tests can stop. It depends purely on when
all responses are recieved.
Load tests stop when a fixed number of requests per driver node are run in
parallel. There is no time bound, as this cannot be controlled by the load
testing tool, but rather depends on the implementation of the Target Server.

The system must support observability

The Orchestrator node must know how many requests each driver node has sent,
updated at a maximum interval of one second
The Orchestrator node must be able to show a dashboard with aggregated {min,
max, mean, median, mode} response latency across all (driver) nodes, and for
each (driver) node
Both the driver node and the orchestrator node must have a metrics store.
It is up to you to choose how this is implemented, but all your metrics from
testing must reside here.
The system must be scalable

It should be possible to run a test with a minimum of three (one
orchestrator, two driver) and a maximum of nine (one orchestrator, 8 driver)
nodes.
It should be possible to change the number of driver nodes between tests.
Code
An implementation of an Orchestrator Node

Exposes a REST API to view and control different tests
Can trigger a load test
Can report statistics for a current load test
Implement a Runtime controller that
Handles Heartbeats from the Driver Nodes (sent after the Driver Nodes
have been connected and until they are disconnected)
Is responsible for co-ordinating between driver nodes to trigger load
tests
recieves metrics from the driver nodes and stores them in the metrics
store
An implementation of a Driver node

Sends requests to the target webserver as indicated by the Orchestrator
node
records statistics for {mean, median, min, max} response time
sends said results back to the Orchestrator node
Implements a communication layer that talks to the central Kafka instance,
implemented around a Kafka Client.
An implementation of a target HTTP server

An endpoint to test (/ping)
A metrics endpoint to see the number of requests sent and responses sent
(/metrics)
You can find a sample implementation of a target server here, which you can use
for your initial testing. This comes with both the /ping and /metrics
endpoints baked in -
https://github.com/anirudhRowjee/bd2023-load-testing-server


// Register message format
{
  "node_id": "<NODE ID HERE>",
  "node_IP": "<NODE IP ADDRESS (with port) HERE>",
  "message_type": "DRIVER_NODE_REGISTER"
}
The Orchestrator node must publish a message to the test_config topic to send
out test configuration to all driver nodes

// testconfig message format
{
  "test_id": "<RANDOMLY GENERATED UNQUE TEST ID>",
  "test_type": "<AVALANCHE|TSUNAMI>",
  "test_message_delay": "<0 | CUSTOM_DELAY (only applicable in place of Tsunami testing)>",
  "message_count_per_driver": "<A NUMBER>"
}
The Orchestrator node must publish a message to the trigger topic to begin the
load test, and as soon as the drivers recieve this message, they have to begin
the load test

// trigger message format
{
  "test_id": "<RANDOMLY GENERATED UNQUE TEST ID>",
  "trigger": "YES"
}
The driver nodes must publish their aggregate metrics to the metrics topic as
the load test is going on at a regular interval

// metrics message format
{
  "node_id": "<RANDOMLY GENERATED UNQUE TEST ID>",
  "test_id": "<TEST ID>",
  "report_id": "<RANDOMLY GENERATED ID FOR EACH METRICS MESSAGE>",
  // latencies in ms
  "metrics": {
    "mean_latency": "",
    "median_latency": "",
    "min_latency": "",
    "max_latency": ""
  }
}
The driver nodes must also publish their heartbeats to the heartbeat topic as
the load test is going on at a regular interval

// heartbeat message format
{
  "node_id": "<RANDOMLY GENERATED UNQUE TEST ID>",
  "heartbeat": "YES",
  "timestamp": "<Heartbeat Timestamp>"
}



• Orchestrated collaboration among 8 driver nodes for distributed load testing.
• Utilized Kafka for communication, employing publish-subscribe architecture.
• Ensured highly concurrent, high-throughput load tests on web servers.
• Leveraged efficient coordination and communication between nodes.
