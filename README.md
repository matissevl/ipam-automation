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
│   │   │   ├── scripts
│   │   │   │   ├── clear_data.py
│   │   │   │   └── import_data.py
│   │   │   └── tasks
│   │   │       └── main.yml
│   │   └── nipap_installer
│   │       ├── files
│   │       │   ├── httpd
│   │       │   └── nipap
│   │       ├── tasks
│   │       │   ├── main.yml
│   │       │   └── main.yml.updates
│   │       └── templates
│   │           └── nipap.conf.j2
│   └── site.yml
├── custom-vagrant-hosts.yml
├── LICENSE
├── README.md
├── README.md.bak
├── scripts
│   ├── measure_latency_netbox.py
│   ├── measure_latency_nipap.py
│   ├── verify_password_netbox.py
│   └── verify_password_nipap.py
├── Vagrantfile
├── vagrant-groups.yml
├── vagrant-hosts.yml
```

## Start the VMs

Before starting the VMs, edit the `vagrant-groups.yml` and `vagrant-hosts.yml` files as needed.

This command will create and provision two VMs: one for NetBox and one for NIPAP.

## Provision the VMs with Ansible

Vagrant will automatically run the Ansible playbooks to install and configure NetBox and NIPAP. Instructions for setting up the machines, configuring them, and configuring their Ansible groups can be found at [https://github.com/bertvv/ansible-skeleton](https://github.com/bertvv/ansible-skeleton).

## Access the Applications

- **NetBox**: Access NetBox by navigating to `http://<netbox-vm-ip>` in your web browser.
- **NIPAP**: Access NIPAP by navigating to `http://<nipap-vm-ip>` in your web browser.

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

- **netbox**: Contains tasks to install and configure NetBox.
- **nipap**: Contains tasks to install and configure NIPAP.

## Contributing

Feel free to submit issues, fork the repository and send pull requests!

## License

This project is licensed under the MIT License.
