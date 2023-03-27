# Contributing

We appreciate your interest in contributing to this F5 Professional Services repository. Thank you!

**Read our Code of Conduct**

Read our [Community Code of Conduct](https://github.com/f5devcentral/f5-professional-services/blob/main/code_of_conduct.md) to keep our community approachable and respectable.

**Finding good first issues**

You can find beginner-friendly issues in this repository [here](https://github.com/f5devcentral/f5-professional-services/issues). 

**Reporting an issue**

If you believe that you have found a new bug or wants to suggest an enhancement, you should report it by creating a new issue in the [f5devcentral/f5-professional-services](https://github.com/f5devcentral/f5-professional-services/issues) issue tracker.

## Style guides, naming convention and security

When submitting your contribution, please, adhere to the following style guides, recommended practices and naming convention.

**Security**

Before submit your contribution, please make sure at mininum:
- There is no credential inside your code
- There is no API key inside your code
- There is no license key inside your code
- There is no reference to any internal company document, IP addresses, email

**README files**

Lots of sections in this repository require a README file, particularly Ansible Playbooks, Terraform Plans, or other tools written in different languages.  

Consider using this [sample](https://github.com/f5devcentral/f5-professional-services/blob/main/sample_readme.md) as a starting point for your README file. 

Also, check [awesome-readme](https://github.com/matiassingers/awesome-readme) for great examples.

Update your contribution in the top-level README (alpha-order) of your folder if there is one.

**Ansible Playbooks**

- Style Guides

When writing your playbook, consider the following Ansible Playbooks Best Practices and Tips and Tricks manual

https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html  
https://docs.ansible.com/ansible/2.9/user_guide/playbooks_best_practices.html  

Please do not upload a hosts file.
Ensure any provider information is generalized or variablized.
If supporting JSON is required, ensure the contents are generalized, and that the file path for the JSON is relative. Ideally reference json in the same directory as the yaml to make reading the example in github easier.

- Naming Convention

Consider naming your Ansible Playbook folder and files using the technology noun as the prefix and action as the suffix:  
*f5_big-ip_upgrade*  
*f5_big-ip_generate_qkview*  
*f5_big-ip_asm_update_signatures*  
*f5_rseries_build_tenant*  

**Python**

- Style Guides

When writing any Python code, refer to the following Python code style:

https://peps.python.org/pep-0008/  

When writing an one-off script, use the following application layout:

https://realpython.com/python-application-layouts/

```helloworld/  
│  
├── .gitignore  
├── helloworld.py  
├── LICENSE  
├── README.md  
├── requirements.txt  
├── setup.py  
└── tests.py  
```` 
- Naming Convention

If you are sending a Python code it's likely you are submitting a tool to our *tools* section. Consider naming it using the technology noun as the prefix and action as the suffix:   
*f5-ltm-report-vs-statistics*  
*f5-ltm-rename-objects*
*f5-xc-export-csv*

**F5 iRules / iRulesLX**

- Style Guides

When submitting iRules, consider the following as recommended practices:

https://community.f5.com/t5/technical-articles/irules-style-guide/ta-p/305921  
https://community.f5.com/t5/technical-articles/avoiding-common-irules-security-pitfalls/ta-p/306623  
https://community.f5.com/t5/technical-articles/irules-optimization-101-05-evaluating-irule-performance/ta-p/277028  

- Naming Convention

Consider the following naming convention. If the iRule submitted also need data-groups, submit it using a folder with the same name of the iRule:  

*irule-ltm-http-rewrite.tcl*  
*irule-dns-dynamic-response.tcl*  
*irule-asm-custom-blocking-page.tcl*  

## Code reviews and pull request

All code submissions require review. GitHub Pull Requests are used for this purpose. Please, consult
[GitHub Help](https://help.github.com/articles/about-pull-requests/) for more
information on it.

Please, submit one pull request per major item and name it properly. 

As an example:
Title with a short informative summary of the pull request - (e.g. Adding f5-big-ip-tool-xyz)  
Description: Add details explaining the PR for the reviewer  
