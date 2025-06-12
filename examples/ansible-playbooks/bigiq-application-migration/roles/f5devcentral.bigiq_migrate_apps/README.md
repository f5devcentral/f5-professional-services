# Ansible Role: bigiq_migrate_apps

Performs a series of steps needed to Migrate AS3 application service(s) with its referenced objects from a BIG-IP to another BIG-IP.

Examples:
- Migration from a BIG-IPs on Premise to Public Cloud.
- Migration from legacy BIG-IP platforms to new platforms.
- Migration from a not reachable BIG-IP to a replacement BIG-IP.

# Prerequisites

- Install following galaxy roles:
  - ``ansible-galaxy install f5devcentral.atc_deploy --force``
  - ``ansible-galaxy install f5devcentral.bigiq_pinning_deploy_objects --force``
  - ``ansible-galaxy install f5devcentral.bigiq_move_app_dashboard --force``

- Both devices need to be managed by BIG-IQ
- ALL referenced objects must be managed on BIG-IQ
- Referenced objects must be located in /Common and have a unique name across BIG-IQ
- Referenced objects supported: 
  - SSL Certificate and Key (must be managed on BIG-IQ ([more info](https://techdocs.f5.com/en-us/bigiq-7-1-0/managing-big-ip-devices-from-big-iq/ssl-certificates.html)))
  - Security Logging Profile
  - WAF Policy

If you are interested for other type of objects, [open an issue on GitHub](https://github.com/f5devcentral/ansible-role-bigiq_migrate_apps/issues).

# Limitations

- Migration of AS3 application services only
- Migration is per AS3 tenants
- Migration of 1 tenant at a time
- App services have to be migrated to a **new tenant** (same tenant name not supported)
- AS3 ``/Common/shared`` tenant not supported

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

Define the variables to migrate AS3 application services from a tenant to a new BIG-IP device.

      # Working directory to store migration files on your local machine
      dir_as3: ~/tmp 

      # BIG-IP device source where tenant_to_migrate is located
      device_address: 10.1.1.8
      tenant_to_migrate: datacenter1

      # Target BIG-IP device where the tenant will be migrated
      new_device_address: 10.1.1.7 
      new_tenant_name: us-east-1
      
      # Name of the Application in BIG-IQ Dashboard which will contain the migrated App Services
      new_bigiq_app_name: "App Services migrated"
      
      # OPTIONAL: Replace virtual server within the tenant
      new_virtual_servers: 
        - { old: "10.1.10.101", new: "192.168.1.101" }
        - { old: "10.1.10.102", new: "192.168.1.102" }
        
      # OPTIONAL: Remove old tenant - false by default
      remove_old_tenant: false

      # OPTIONAL: If the device hosting the original application services is no longer reachable
      old_device_not_reachable: false

      # OPTIONAL: Execute each step independantly - false by default
      deploy_objects_only: false
      or
      deploy_as3_only: false
      or
      cleanup_only: false

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
          - name: Migrate AS3 application service(s) from a BIG-IP to another.
            include_role:
              name: f5devcentral.bigiq_migrate_apps
            vars:
              dir_as3: ~/tmp
              device_address: 10.1.1.8
              tenant_to_migrate: datacenter1
              new_device_address: 10.1.1.9
              new_tenant_name: us-east-1
              new_bigiq_app_name: "App Services migrated"
            register: status

## License

Apache

## Author Information

This role was created in 2020 by [Romain Jouhannet](https://github.com/rjouhann).

[1]: https://galaxy.ansible.com/f5devcentral/bigiq_pinning_deploy_objects

