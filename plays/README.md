# Ansible Plays

This includes sample plays for cassandra, elasticsearch, mongodb etc. Among these I am actively maintaining playbooks for elasticsearch.

## Elasticsearch

In elasticsearch directory you will find many playbooks with different functionalities. In inventory file(development.ini or production.ini or test.ini or /etc/ansible/hosts) I include hosts in groups with group names in specific pattern. eg.

    [sample_elasticsearch_monitoring]
    x.x.x.x
    [sample_elasticsearch_master]
    a.a.a.a
    b.b.b.b
    c.c.c.c    
    [sample_elasticsearch_data]
    d.d.d.d
    [sample_kibana]
    k.k.k.k
    [sample_logstash]
    l.l.l.l
    [sample:children]
    sample_elasticsearch_master
    sample_elasticsearch_data
    sample_kibana
    sample_elasticsearch_monitoring
    sample_logstash

Where sample is the cluster_name.

#### 1.  create_mount_points.yml

   This playbook uses ansible-disk role. It is useful when you want to configure volumes with filesystem and create mountpoint. I use this playbook when I want to create volumes on data nodes.
   eg.

        roles:
            - ansible-disk
         vars:
             disk_additional_disks:
             - disk: /dev/nvme0n1
               fstype: ext4
               force: yes
               mount_options: defaults
               mount: /data0
               part: /dev/nvme0n1p1

#### 2.  ec2_launch.yml & ec2_terminate.yml

    These are helper playbooks to create and terminate ec2 instances. They are very helpful when you want to quickly create test environment and terminate them at the end of the tests.


#### 3.  install_elasticsearch.yml

   This playbook will install elasticsearch cluster as well as single node external monitoring cluster. It will also install kibana on client/kibana node and on monitoring cluster. To run this playbook you can either pass following options as extra variables(--extra-vars or -e) to ansible-playbook command.

        cluster_name: sample
        all_data: /usr/app/elastic
        es_major_version: 6.x
        es_version: 6.1.0
        admin_pass: changeme
        kibana_pass: changeme
        monitor_pass: changeme
        es_box_type: strong

By default, this playbook will calculate all_data to be comma separated list of all the mountpoints other than '/'(root partition). Once the whole stack is installed you can use kibana to login using username ***elastic*** and password ***admin_pass*** (in above example username:elastic and password: changeme), then you can create users and change passwords for other users using user management.

es_box_type can be used to create cluster will different node profile. It is useful to create cluster with Hot/Warm architecture. You can also specify this variable in inventory for each node.

If you want to specify extra options like email account settings or settings related to AD authentication etc., you can set them as a group variable es_config_group(please refer group_vars part). eg. for sample cluster, create sample dir in group_vars directory and then create sample.yml file inside it. Add following content in sample.yml, this will be used by ansible as part of group variable for sample cluster.

       es_config_group: {
         xpack.notification.email.account.exchange_account.profile: outlook,
         xpack.notification.email.account.exchange_account.email_defaults.from: noreply@example.com,
         xpack.notification.email.account.exchange_account.email_defaults.reply_to: noreply@example.com,
         xpack.notification.email.account.exchange_account.smtp.auth: false,
         xpack.notification.email.account.exchange_account.smtp.starttls.enable: false,
         xpack.notification.email.account.exchange_account.smtp.host: smtp.example.com,
         xpack.notification.email.account.exchange_account.smtp.port: 25
      }

eg. we can run following command to create sample cluster.

    ansible-playbook elasticsearch/install_elasticsearch.yml -i ../production.ini --extra-vars "cluster_name=sample admin_pass=changeme monitor_pass=changeme es_major_version=6.x es_version=6.1.1 kibana_pass=changeme all_data=/usr/app/elastic"

#### 4. install_elasticsearch_opensource.yml

This playbook is similar to install_elasticsearch.yml, the only difference is it will install opensource version of EK stack. It will also install x-pack with basic monitoring. Monitoring data will be sent to the same cluster(no dedicated monitoring cluster)

eg. we can run following command to create opensource sample elasticsearch cluster.

    ansible-playbook elasticsearch/install_elasticsearch.yml -i ../production.ini --extra-vars "cluster_name=sample es_major_version=6.x es_version=6.1.1 all_data=/usr/app/elastic"

#### 5. install_kibana.yml

This is standalone playbook which will just install kibana on specific host/group.

#### 6. install_logstash.yml

This playbook will install logstash on the nodes in {{cluster_name}}_logstash group, i.e. in our example, sample_logstash group. Please refer README for [ansible-role-logstash]( https://github.com/shribigb/ansible-role-logstash) role.

#### 7. rolling_upgrade_elasticsearch.yml

This role is work in progress.
