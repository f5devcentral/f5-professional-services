# Ansible Role: bigiq_pinning_deploy_objects

Performs a series of steps needed to pin or unpin, then deploy BIG-IQ object(s) to a BIG-IP device managed on BIG-IQ.

This role currently supports only SSL Certificates & Keys, iRule, WAF Policy and Security Logging Profiles.

If you are interested for other type of objects, [open an issue on GitHub](https://github.com/f5devcentral/ansible-role-bigiq_pinning_deploy_objects/issues).

This role is perfect to use along with [F5 automation tool chain (ATC) deploy declaration](https://galaxy.ansible.com/f5devcentral/atc_deploy) galaxy role used 
to deploy AS3 application services with BIG-IQ.

*Note: When unpining objects, the removal of those objects cannot be done with this role. It is recommended to use the BIG-IQ Evaluate & Deploy along with the following options, Source Scope: All Changes, Unused Objects: Remove Unused Objects.*

Want to execute the role on BIG-IQ itself? [f5-bigiq-ansible-runner](https://github.com/f5devcentral/f5-big-iq-pm-team/tree/master/f5-bigiq-ansible-runner).

## Role Variables

Available variables are listed below. For their default values, see `defaults/main.yml`.

Establishes initial connection to your BIG-IQ. These values are substituted into
your ``provider`` module parameter. These values should be the connection parameters
for the **CM BIG-IQ** device.

        provider:
          user: admin
          server: 10.1.1.4
          server_port: 443
          password: secret
          auth_provider: tmos
          validate_certs: false

Define the list of existing objects you want to pin and deploy.

    modules: 
      - name: ltm
        pin:
          - { type: "sslCertReferences", name: "demo1.crt" }
          - { type: "sslKeyReferences", name: "demo1.key" }
          - { type: "iruleReferences", name: "myIrule" }
        unpin:
          - { type: "sslCertReferences", name: "demo2.crt" }
          - { type: "sslKeyReferences", name: "demo2.key" }

      - name: asm
        pin:
          - { type: "attachedPoliciesReferences", name: "myWAFpolicy1" }
          - { type: "attachedPoliciesReferences", name: "myWAFpolicy2" }
      - name: shared_security
        pin:
          - { type: "logProfileReferences", name: "mySecurityLoggingProfile" }

Define the target device where you want to pin and deploy the objects.
It can be either device_address or device_name.
If you are deploying to a HA pair, only specify one of the device address or name, the role will push automatically to 
all the devices part of the cluster (supports only clusters with 2 devices).

    device_address: 10.1.1.7

or

    device_name: bigip.example.com

Define the deployment Task Name (optional):

    bigiq_task_name: "Deployment through Ansible/API"

## Example Playbook

    ---
    - hosts: all
      connection: local
      vars:
        provider:
          user: admin
          server: "{{ ansible_host }}"
          server_port: 443
          password: secret
          auth_provider: tmos
          validate_certs: false

      tasks:
          - name: Pin or unpin and deploy SSL certificate & key, WAF policy and Security Logging Profile to device
            include_role:
              name: f5devcentral.bigiq_pinning_deploy_objects
            vars:
              bigiq_task_name: "Deployment through Ansible/API"
              device_address: 10.1.1.7
              skip_deploy: false # set to true to skip deployment of the change(s) and only do the pin/unpin action
              modules: 
                - name: ltm
                  pin:
                    - { type: "sslCertReferences", name: "demo1.crt" }
                    - { type: "sslKeyReferences", name: "demo1.key" }
                    - { type: "iruleReferences", name: "myIrule" }
                    - { type: "sslCertReferences", name: "myIrule" }
                  unpin:
                    - { type: "sslCertReferences", name: "demo2.crt" }
                    - { type: "sslKeyReferences", name: "demo2.key" }
                - name: asm
                  pin:
                    - { type: "attachedPoliciesReferences", name: "myWAFpolicy1" }
                    - { type: "attachedPoliciesReferences", name: "myWAFpolicy2" }
                - name: shared_security
                  pin:
                    - { type: "logProfileReferences", name: "mySecurityLoggingProfile" }
            register: status

## License

Apache

## Author Information

This role was created in 2022 by [Romain Jouhannet](https://github.com/rjouhann).

[1]: https://galaxy.ansible.com/f5devcentral/bigiq_pinning_deploy_objects
