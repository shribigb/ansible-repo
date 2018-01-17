# Ansible Role: Kibana

[![Build Status](https://travis-ci.org/geerlingguy/ansible-role-kibana.svg?branch=master)](https://travis-ci.org/geerlingguy/ansible-role-kibana)

An Ansible Role that installs Kibana(5.x & 6.x) on RedHat/CentOS or Debian/Ubuntu.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

    kibana_server_port: 5601
    kibana_server_host: "0.0.0.0"

The FQDN or IP address and port Kibana should use.

    kibana_elasticsearch_url: "http://localhost:9200"

The URL (including port) over which Kibana will connect to Elasticsearch.

    kibana_elasticsearch_username: kibana
    kibana_elasticsearch_password: changeme

Specify username and password of kibana user which kibana will use to connect to security enabled elasticsearch.

    kibana_major_version: "6.x"

Kibana major version, it can be either 5.x or 6.x

    kibana_version: "6.1.0"

Specify specific version you want to install

    kibana_enable_xpack: false

Specify if you want to enable xpack for kibana

    kibana_extra_conf: { }

If you want to set any additional configuration options please add here.

    kibana_plugin_reinstall: false

If you want to reinstall plugins in a re-run, set this variable to true.

## Dependencies

None.

## Example Playbook

    - hosts: kibana
      roles:
        - ansible-role-kibana

## License

MIT / BSD

## Author Information

This role was created in 2014 by [Jeff Geerling](https://www.jeffgeerling.com/), author of [Ansible for DevOps](https://www.ansiblefordevops.com/). This role is then modified by [Shri Bodas](https://github.com/shribigb) in 2018.
