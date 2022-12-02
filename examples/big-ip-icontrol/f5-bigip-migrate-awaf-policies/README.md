# f5-bigip-migrate-awaf-policies
## Overview 

A *Postman Collection* to migrate all AWAF policies from one BIG-IP device to another. 

# How To Use

1. (Optional) Create a new workspace on *Postman*.

2. Import the *Postman Collection* (*f5-bigip-migrate-awaf-policies.postman_collection.json*)

    ![Import Postman Collection](https://github.com/pedrorouremalta/f5-bigip-migrate-awaf-policies/blob/main/images/image001.png)

3. Import the *Postman Environment* (*f5-bigip-migrate-awaf-policies.postman_environment.json*)

    ![Import Postman Environment](https://github.com/pedrorouremalta/f5-bigip-migrate-awaf-policies/blob/main/images/image002.png)

4. Configure the *Postman Environment* imported:

    ![Configure Postman Environment](https://github.com/pedrorouremalta/f5-bigip-migrate-awaf-policies/blob/main/images/image003.png)

5. Run the *Postman Collection* (make sure the Environment imported is selected):

    ![Run Postman Collection 1](https://github.com/pedrorouremalta/f5-bigip-migrate-awaf-policies/blob/main/images/image004.png)

    ![Run Postman Collection 2](https://github.com/pedrorouremalta/f5-bigip-migrate-awaf-policies/blob/main/images/image005.png)

6. Follow the logs on the *Postman Console*: 

    ![Postman Console 1](https://github.com/pedrorouremalta/f5-bigip-migrate-awaf-policies/blob/main/images/image006.png)

    ![Postman Console 2](https://github.com/pedrorouremalta/f5-bigip-migrate-awaf-policies/blob/main/images/image007.png)

    **Note**: When a AWAF policy already exists in the target device it will be replaced. 

    ![Postman Console 3](https://github.com/pedrorouremalta/f5-bigip-migrate-awaf-policies/blob/main/images/image008.png)
