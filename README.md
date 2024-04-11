Big Data Project 2023 @ PES University - Distributed Load Testing System
Goal
Design and build a distributed load-testing system that co-ordinates between
multiple driver nodes to run a highly concurrent, high-throughput load test on a
web server. This system will use Kafka as a communication service.

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

Implementation Guidelines
The preferred language of implementation is Golang as it is the industry's
choice for building distributed systems. However, you are also free to use
other languages such as Python, Java, C# and C++ to do the same. Marks will be
awarded based on your implementation, thought process, architecture, and
effort, not on the language.
The concept of Heartbeat has been covered in the course.
Feel free to use any available distributed system primitives (not full
applications such as RabbitMQ) to further ease your development process.
The JSON Message Format has been provided for your reference, and is intended
to help you get started with implementation. You are free to modify it as you
see fit, so long as it does not prevent you from implementing a part of the
project properly.
Weekly Guidelines
Week 1 Target: Single Orchestrator, Two Drivers with

Avalanche and Tsunami testing coverage
Week 2 Target: Single Orchestrator, Two Drivers

All features mentioned in the week 1 target
metrics reporting
Week 3 Target: Single Orchestrator with eight drivers

All features mentioned in week 2 target
Metrics dashboard and CLI or GUI Control interface
A maximum of one second latency for dashboard / metrics update from the
orchestrator node
JSON Message and Topic Descriptor Format
All Nodes must register themselves through the register topic

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
