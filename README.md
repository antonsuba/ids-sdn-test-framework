# IDS SDN Test Framework

## Setup

1. Clone repository into Mininet VM home directory

2. Copy contents of `pox_components` into `~/pox/ext`, along with other POX components you want to use

3. For training models, place the folder containing the training dataset inside `ml_ids/training_data`

4. For validating models, place the folder containing the validation dataset inside `ml_ids/validation_data`

5. Place your custom model training and validation scripts inside the `ml_ids` folder

6. If you have your own models, you may place them inside `ml_ids/ids_models`

7. Place PCAP files inside the `pcap` folder

8. If you have your own Python modules for the internal and external network generation, you may place them inside `network/internal_network` and `network/external_network` respectively

9. Place your custom test case scripts inside the `test_cases` folder

10. Configure framework using the provided config file: `config/config.yml`

11. Place an `attack_hosts.txt` file inside the `config` folder that contains the total number of hosts in the first line, and the attack host IP addresses for the next succeeding lines

## Usage

The framework must have been set up and configured accordingly before it can be used.

### Training Models

Run this command in the terminal:

```bash
python tool.py train
```

### Validating Models

Run this command in the terminal:

```bash
python tool.py validate
```

### Generating Test Network

1. Start POX one terminal.

2. In another terminal, run this command:

    ```bash
    python tool.py createnetwork
    ```

### Running Tests

The steps are the same with generating the test network, except that several parameters are passed to the createnetwork command.

Run:

```bash
python tool.py createnetwork exectest TestCase1 TestCase2  # TestCase3, ...
```

where the parameters after exectest are the names of the test case classes found in the `test_cases` folder.

Results of the tests can be found in `results/ids_test_results.txt`

## Creating Custom Test Cases

Making your own test cases is easy. Just create a class that inherits from the TestCase object in `test_cases/test_case.py`. Simply override the

```python
def _exec_test(self, targets, int_hosts, ext_hosts, int_switches, ext_switches, int_routers, ext_routers)
```

method and execute your tests there.

Parameter    | Description
------------ | -------------------------
targets      | List of target hosts
int_hosts    | List of internal hosts
ext_hosts    | List of external hosts
int_switches | List of internal switches
ext_switches | List of external switches
int_routers  | List of internal routers
ext_routers  | List of external routers

See the provided `ddos.py` test case for reference.

## Creating Custom Networks

Create a class in either the `internal_network` or `external_network` that implements this method:

```python
def create_topo(self, topo, main_switch, mac_ip_list)
```

The framework then uses this module as the basis of the network topology

Parameter    | Description
------------ | -------------------------
topo         | Mininet topo object
main_switch  | Name of main connecting switch. Serves as bridge both networks
mac_ip_list  | Dictionary of mac ip pairs


Router configuration is done by implementing:

```python
def configure_router(self, routers)
```

Parameter    | Description
------------ | -------------------------
routers      | List of all router nodes in the network


## Other Tools

### Scripts

1. The `scripts/extract_attack_hosts.py` script allows you to generate the `attack_scripts.txt` file automatically. Just modify it to use your training dataset.

2. The `scripts/extract_ip_mac.sh` script produces the MAC-IP address pairs, given a PCAP file. Just run the script with the PCAP file as the first parameter.