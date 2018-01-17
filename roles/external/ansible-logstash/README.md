# Ansible Role: Logstash

[![Build Status](https://travis-ci.org/geerlingguy/ansible-role-logstash.svg?branch=master)](https://travis-ci.org/geerlingguy/ansible-role-logstash)

An Ansible Role that installs Logstash(5.x & 6.x) on RedHat/CentOS Debian/Ubuntu.

## Requirements

Though other methods are possible, this role is made to work with Elasticsearch as a backend for storing log messages.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):


    logstash_elasticsearch_hosts:
      - http://localhost:9200

The hosts where Logstash should ship logs to Elasticsearch.

    logstash_ssl_dir: /etc/pki/logstash
    logstash_ssl_certificate_file: logstash-forwarder-example.crt
    logstash_ssl_key_file: logstash-forwarder-example.key

Local paths to the SSL certificate and key files, which will be copied into the `logstash_ssl_dir`.

For utmost security, you should use your own valid certificate and keyfile, and update the `logstash_ssl_*` variables in your playbook to use your certificate.

To generate a self-signed certificate/key pair, you can use use the command:

    $ sudo openssl req -x509 -batch -nodes -days 3650 -newkey rsa:2048 -keyout logstash.key -out logstash.crt

Note that filebeat and logstash may not work correctly with self-signed certificates unless you also have the full chain of trust (including the Certificate Authority for your self-signed cert) added on your server. See: https://github.com/elastic/logstash/issues/4926#issuecomment-203936891

    logstash_enabled_on_boot: yes

Set this to `no` if you don't want logstash to run on system startup.

    logstash_install_plugins:
      - logstash-input-beats

A list of Logstash plugins that should be installed.

    logstash_enable_xpack: true

Set this to false if you don't to install x-pack

    logstash_heap_size: 1g

This will set logstash's heap to 1g.

    logstash_major_version: 6.x

This can be either 5.x or 6.x

    logstash_version: 6.1.0

Specify specific version of logstash you want to install

    logstash_xpack_monitoring_enable: true

Set this to true if you want to enable logstash monitoring in elasticsearch. If this is set to true you have to specify logstash_system_username & logstash_system_password.

    logstash_system_username: logstash_system
    logstash_system_password: changeme

If you want to enable logstash management in elasticsearch you have to set logstash_xpack_management_enable to true:

    logstash_xpack_management_enable: true

If above option is set then you have to specify logstash_admin_username, logstash_admin_password & logstash_management_pipeline_id_list

    logstash_admin_username: logstash_admin
    logstash_admin_password: changeme
    logstash_management_pipeline_id_list: ['id1', 'id2', 'id3']

You can specify logstash_path_data and logstash_path_log options to change default values of path.data and path.log respectively.

    logstash_install_conf: true
    logstash_conf_src_path: <directory path containing conf files>

If you want to install custom logstash configuration files you can specify logstash_install_conf to true and specify local path of the directory where configuration files are located. This role will install all the files in this directory to /etc/logstash/conf.d/ directory.

    logstash_install_dictionary: true
    logstash_dictionary_src_path: dictionary
    logstash_dictionary_dst_path: /etc/logstash/dictionary

If you want to install custom dictionary for translate filter, set logstash_install_dictionary to true. Also, specify local path of directory where all the directory files are located. Also specify destination of the dictionary on remote logstash host.

    logstash_extra_conf_options: {
      pipeline.workers: 24,
      config.reload.automatic: true,
      queue.type: persisted,
      queue.page_capacity: 1gb,
      queue.max_bytes: 150gb,
      queue.checkpoint.acks: 0,
      queue.checkpoint.writes: 0,
      queue.checkpoint.interval: 10000
    }

If you want to add any other custom configurations, specify them under logstash_extra_conf_options variable. This role will add these options in logstash.yml file at the target logstash host.

## Other Note

This role also adds LS_HOSTNAME environment variable in /etc/defaults/logstash which can be usable inside your logstash configuration files. It's very useful if you want to add logstash host information in elasticsearch document.

## Example Playbook

    - hosts: search
      roles:
        - ansible-role-logstash

## License

MIT / BSD

## Author Information

This role was created in 2014 by [Jeff Geerling](https://www.jeffgeerling.com/), author of [Ansible for DevOps](https://www.ansiblefordevops.com/).
This role is then modified by [Shri Bodas](https://github.com/shribigb) in 2018.
