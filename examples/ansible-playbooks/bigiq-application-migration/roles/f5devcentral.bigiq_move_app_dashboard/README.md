# Ansible Role: bigiq_move_app_dashboard

Performs a series of steps needed to move Application Service(s) within the BIG-IQ application 
dashboard.

This supports any type of applications such as AS3 or legacy application services.

This role is perfect to use along with [F5 automation tool chain (ATC) deploy declaration](https://galaxy.ansible.com/f5devcentral/atc_deploy) galaxy role used 
to deploy AS3 application services with BIG-IQ.

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

Define the list of application and application services as you wish it to be grouped on the 
BIG-IQ application dashboard.

    apps: 
    - name: App1
      pin:
        - name: tenant1_app_service_1
        - name: tenant1_app_service_2
    - name: App2
      pin:
        - name: tenant2_app_service_1
        - name: tenant2_app_service_2

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
          - name: Move AS3 application service(s) in BIG-IQ application dashboard.
            include_role:
              name: f5devcentral.bigiq_move_app_dashboard
            vars:
                apps: 
                - name: App1
                  pin:
                    - name: tenant1_app_service_1
                    - name: tenant1_app_service_2
                - name: App2
                  pin:
                    - name: tenant2_app_service_1
                    - name: tenant2_app_service_2
            register: status

## License

Apache

## Author Information

This role was created in 2020 by [Romain Jouhannet](https://github.com/rjouhann).

[1]: https://galaxy.ansible.com/f5devcentral/bigiq_pinning_deploy_objects

