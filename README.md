# delta-node

Delta node is the node in the distributed delta network. 
A delta node can act as a task runner which receives task from other network and execute it, or as a task coordinator which submits task to the delta network and coordinate with other nodes participated in the task, or both.

A delta node is designed to manage local dataset, and all computation will be done on local dataset. Only encrypted computation result will be uploaded, local dataset will never leak out.

Each delta node will connect to a delta-chain-connector, and almost all the communication with other nodes in the network is proxyed by the connector. Only computation result and secret shares will be transfered between delta nodes in consideration of security and efficiency.

The task which delta node can execute is written in python, with lib [pytorch](https://pytorch.org/) and [delta](https://github.com/delta-mpc/delta-task).

# run delta-node from source code

First git clone this repo.

Then install the package from source code.

```bash
cd delta-node
pip install -r requirements.txt
pip install -e .
```

It is preferred to install the package in a seperate python virtual environment to avoid package version conflict.

## configuration 

We need to configure delta-chain-connector before start it. Run this command to initialize the config file:

```bash
delta_node_start init
```

Then we will see a directory called `config` is created, and in `config` directory, there is a config file called `config.yaml`.

The config file looks like: 

```yaml

# configuration of log
log:  
  # log level
  level: "INFO"
  # directory for log file
  dir: "logs"

# database connection string. here use sqlite for example, and the sqlite database file is db/delta.db
db: "sqlite+aiosqlite:///db/delta.db"

# configuration of connector
chain_connector:
  # connector host
  host: ""
  # connector port
  port: 4500

# configuration of node http server
node:
  # node name
  name: "node1"
  # node public URL
  url: "http://127.0.0.1:6700"

# port of node api server
api_port: 6700

# directory for intermediate data and results of task, here is in task for example
task_dir: "task"

# directory for local dataset, here is in data for example
data_dir: "data"

```

There are two items must be edited. The first one is the `chain_connector.host` and `chain_connector.port` which means host and port of the delta chain connector node connect to, respectively. The second one is the `node.url` which means the public URL of the node. The URL will be published to the delta network after the node joins in delta network, and other nodes will communicate with this node by the URL. The URL should have http or https protocol scheme.

After completing edition of the configuration file, we can start delta node now.

## start delta-node

Enter the following command

```bash
delta_node_start run
```

The node will be started.

# run delta-node from docker

We have built the docker image of delta-node and you can run it from docker for convenience.

First, pull the docker image:

```bash
docker pull deltampc/delta-node:0.3.0
```

and then make a directory as the root dir of the connector.

```bash
mkdir delta-node
cd delta-node
```

## configuration

Run this command to generate the default configuration file.

```bash
docker run -it --rm -v ${PWD}:/app deltampc/delta-node:0.3.0 init
```

In this command, we mount the current directory to the root dir in docker container, and we can see the configuration file created in the docker container.

You will see the configuration file in `config/config.yaml`. You can edit the configuration file as described above.

## start delta chain connector

Enter the following command

```bash
docker run -d --name=delta_node_1 -v ${PWD}:/app -p 6700:6700 deltampc/delta-node:0.3.0
```

In this command, we mount the current directory to the root dir in docker container to set the config file, and bind the 6700 port (the default delta node api port).

The connector will be started.

You can enter this command to see the logs of connector

```bash
docker logs -f chain_connector
```