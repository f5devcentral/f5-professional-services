# Ansible Role: F5 automation tool chain (ATC) deploy declaration

This role deploys declaratives to installed automation tool chain services (AS3, DO, TS) on your BIG-IP or (AS3, DO) on your BIG-IQ. You would use this role to post declarations to the following BIG-IP or BIG-IQ automation tool chain services: application services 3 extension, declaritive onboarding, or telemetry streaming (BIG-IP only). Information regarding these services along with example declaritives is available on [f5-cloud-docs](https://clouddocs.f5.com/).

* note: this role determines which service to use by the referenced declarative which should contain the service class.
For example, AS3 declaratives will contain a service pointer using key "class": with value "AS3" in json declared file [Example](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/declarations/http-services.html#http-with-custom-persistence). Be sure to define service pointers at the beginning of your declaration.

## Requirements

Corresponding ATC service must be installed on BIG-IP or BIG-IQ prior to deploying declaration.

## Role Variables

Available variables are listed below. For their default values, see `defaults/main.yml`:


| Variable             | Required | Default | Example                                                  | Info                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|----------------------|----------|---------|----------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| provider             | yes      | -       | provider: "{{ provider }}"                               | The  **provider**  dictionary is used in the role to define connection details to the BIG-IP in the same way F5 Modules work.                                                                                                                                                                                                                                                                                                                                                                              |
| atc_method           | no       | GET     | atc_method: GET                                          | <li>atc_method accepted values include [POST, GET] for all services, and [DELETE]for AS3 only. <li>atc_deploy role currently does not support AS3 PATCH method.                                                                                                                                                                                                                                                                                                                                            |
| atc_declaration      | yes      | -       | atc_declaration: "{{ lookup('template', 'decl.json') }}" | Mutually exclusive with `atc_declaration_file` and `atc_declaration_url`                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| atc_declaration_file | yes      | -       | atc_declaration_file: "files/decl.json"                  | Mutually exclusive with `atc_declaration` and `atc_declaration_url`                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| atc_declaration_url  | yes      | -       | atc_declaration_url: "https://testurl/as3.json"          | Mutually exclusive with `atc_declaration` and `atc_declaration_file`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| atc_service          | no       | -       | atc_service: AS3                                         | <li>If a declaration is provided, this will auto select based on the payload <li>AS3 <li>Device <li>Telemetry                                                                                                                                                                                                                                                                                                                                                                                              |
| atc_delay            | yes      | 30      | atc_delay: 30                                            | Seconds between retries when checking if an Async call is complete                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| atc_retries          | yes      | 10      | atc_retries: 10                                          | Number times the role will check for a finished task before failing                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| as3_tenant           | no       | -       | as3_tenant: Tenant1                                      | Starting with AS3 3.14.0, you have the option of using POST to the /declare endpoint with a specific tenant in the URI (for example …/declare/tenant1). This only updates the tenant you specified, even if there are other tenants in the declaration. This can be useful in some automation scenarios involving AS3.                                                                                                                                                                                     |
| as3_show             | yes      | base    | as3_show: base                                           | You can use the following URL query parameters for POST, GET, or DELETE Required ``base means``  system returns the declaration as originally deployed (but with secrets like passphrases encrypted), full returns the declaration with all default schema properties populated, expanded includes all URLs, base64s, and other references expanded to their final static values.  <li> Acceptable values include: base, full, expanded                                                                    |
| as3_showhash         | no       | -       | as3_showhash: true                                       | You can use the following URL query parameters for POST (Note: showHash for POST was introduced in AS3 3.14.0 and will only work on 3.14.0 and later):  This was introduced as a protection mechanism for tenants in a declaration (previously you had to use a separate GET request to retrieve the Optimistic lock). If you set “showHash=true”, the results include an optimisticLockKey for each tenant. Attempts to change/update any of the tenants without the correct optimisticLockKey will fail. |
| check_teem           | yes      | true    | check_teem: true                                         | Updates AS3 declaration to include Ansible version for telemetry.                                                                                                                                                                                                                                                                                                                                                                                                                                          |

## Dependencies

None.

## Examples

#### GET AT Declaration

    - name: GET AT Declaration
      hosts: bigip

      tasks:

        - name: ATC GET
          include_role:
            name: atc_deploy
          vars:
            atc_method: GET
            # Select the service as AS3, Device, or Telemetry
            atc_service: AS3
            provider:
              server: 192.168.1.245
              server_port: "443"
              user: admin
              password: admin
              validate_certs: "false"
              auth_provider: tmos

    - debug: var=atc_GET_status


#### POST AT Declaration

    - name: POST AT Declaration
      hosts: bigip

      tasks:

        - name: ATC POST
          include_role:
            name: atc_deploy
          vars:
            atc_method: POST
            atc_declaration: "{{ lookup('template', 'decl.json') }}"
            # atc_declaration_file: files/as3.json
            # atc_declaration_url: "https://testurl/as3.json"
            atc_declaration_file: "files/as3.json"
            atc_delay: 10
            atc_retries: 5
            provider:
              server: 192.168.1.245
              server_port: "443"
              user: admin
              password: admin
              validate_certs: "false"
              auth_provider: tmos

        # atc_AS3_status, atc_DO_status , atc_TS_status
        - debug: var=atc_AS3_status


## License

Apache

## Author Information

This role was created in 2019 by [Greg Crosby](https://github.com/crosbygw).<br>

## Credits

A special thanks to Vinnie Mazza ([@vinnie357](https://github.com/vinnie357)) for the
ansible playbook examples.

