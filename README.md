# NetBox and NIPAP Installation using Vagrant and Ansible

This project sets up two separate virtual machines using Vagrant and Ansible. One VM will host NetBox, and the other will host NIPAP. After the installation, test data will be added to both applications.

## Prerequisites

- [Vagrant](https://www.vagrantup.com/downloads)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

## Project Structure

```plaintext
.
├── ansible
│   ├── group_vars
│   │   ├── all.yml
│   │   ├── netbox.yml
│   │   └── nipap.yml
│   ├── requirements.yml
│   ├── roles
│   │   ├── netbox_generate_data
│   │   │   ├── scripts
│   │   │   │   ├── clear_netbox.py
│   │   │   │   ├── create_ip_addresses.py
│   │   │   │   ├── create_subnets_old.py
│   │   │   │   ├── create_subnets.py
│   │   │   │   ├── create_vlans.py
│   │   │   │   └── create_vrfs.py
│   │   │   └── tasks
│   │   │       └── main.yml
│   │   ├── netbox_insert_data
│   │   │   ├── scripts
│   │   │   │   ├── insert_update_ip_addresses.py
│   │   │   │   ├── insert_update_subnets.py
│   │   │   │   ├── insert_update_vlans.py
│   │   │   │   └── insert_update_vrfs.py
│   │   │   └── tasks
│   │   │       └── main.yml
│   │   ├── nipap_generate_data
│   │   │   ├── scripts
│   │   │   │   └── generate_data.py
│   │   │   └── tasks
│   │   │       └── main.yaml
│   │   ├── nipap_insert_data
│   │   │   ├── tasks
│   │   │   │   └── main.yml
│   │   │   └── templates
│   │   │       ├── clear_data.py.j2
│   │   │       └── import_data.py.j2
│   │   └── nipap_installer
│   │       ├── files
│   │       │   ├── httpd
│   │       │   └── nipap
│   │       ├── tasks
│   │       │   └── main.yml
│   │       └── templates
│   │           └── nipap.conf.j2
│   └── site.yml
├── README.md
├── scripts
│   ├── measure_latency_netbox.py
│   ├── measure_latency_nipap.py
│   ├── verify_password_netbox.py
│   └── verify_password_nipap.py
├── Vagrantfile
├── vagrant-groups.yml
└── vagrant-hosts.yml
```

## Python virtual environment

It is recommended to create a Python virtual environment to install the required Python packages. To create a virtual environment, run the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install ansible pynipap pynetbox
ansible-galaxy install -r ansible/requirements.yml
```

## Start the VMs

Before starting the VMs, edit the `vagrant-groups.yml` and `vagrant-hosts.yml` files as needed.

Then, run the following command to start the VMs:

```bash
vagrant up
```

This command will create and provision two VMs: one for NetBox and one for NIPAP.

## Provision the VMs with Ansible

Vagrant will automatically run the Ansible playbooks to install and configure NetBox and NIPAP. Instructions for setting up the machines, configuring them, and configuring their Ansible groups can be found at [https://github.com/bertvv/ansible-skeleton](https://github.com/bertvv/ansible-skeleton).

## Access the Applications

- **NetBox**: Access NetBox by navigating to `http://<netbox-vm-ip>:8000` in your web browser.
- **NIPAP**: Access NIPAP by navigating to `http://<nipap-vm-ip>:8181` in your web browser.

## Add Test Data

The Ansible playbooks will automatically add test data to both NetBox and NIPAP during the provisioning process.

## Vagrantfile

The Vagrantfile defines two VMs and specifies the Ansible playbooks to run for each VM.

## Ansible Playbooks

- **netbox.yml**: Installs and configures NetBox.
- **nipap.yml**: Installs and configures NIPAP.

## Inventory

The `vagrant-groups.yml` and `vagrant-hosts.yml` files define the inventory for Ansible, specifying the IP addresses of the VMs.

## Roles

- **netbox_generate_data**: Contains scripts and tasks to generate test data for NetBox.
- **netbox_insert_data**: Contains scripts and tasks to insert and update data in NetBox.
- **nipap_generate_data**: Contains scripts and tasks to generate test data for NIPAP.
- **nipap_insert_data**: Contains tasks and templates to insert and update data in NIPAP.
- **nipap_installer**: Contains files, tasks, and templates to install and configure NIPAP.

## Contributing

Feel free to submit issues, fork the repository and send pull requests!

## License

This project is licensed under the MIT License.
