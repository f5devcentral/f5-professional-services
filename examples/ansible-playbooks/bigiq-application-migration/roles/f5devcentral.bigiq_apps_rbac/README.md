# Ansible Role: bigiq_apps_rbac

Performs a series of steps needed to assign or unassign **Application Services Viewer or Manager** roles to user(s) having access to existing top Application object in BIG-IQ.

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

Define the application role name and application service role name.
Look under BIG-IQ **System > Role Management > Roles > Custom Roles > Application Roles** to see the application roles.
The role name is based on the app name + Viewer or Manager. Example below with an Application called `BusinessUnit1` and
an Application Service called `App1_MyHttpService`.

If you specify ``unassign_user`` with a username, the role will unassign the user to the ``application_service_role_name``.

    application_role_name: "BusinessUnit1 Viewer"
    application_service_role_name: "App1_MyHttpService Viewer"
    unassign_user: peter # optional

## Example Playbooks

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
          - name: Assign Application Service role to users with existing Application Role
            include_role:
              name: f5devcentral.bigiq_apps_rbac
            vars:
              application_role_name: "BusinessUnit1 Viewer"
              application_service_role_name: "App1_MyHttpService Viewer"
            register: status


## License

Apache

## Author Information

This role was created in 2020 by [Romain Jouhannet](https://github.com/rjouhann).

[1]: https://galaxy.ansible.com/f5devcentral/bigiq_pinning_deploy_objects

