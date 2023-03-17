# This iRule will allow you to put a list of important security groups in a Data Group then only list those groups in a string as opposed to a very long string with groups you do not care about.
String Type Data Group
/Common/Groupnames
Important_Group_1 = ""
Important_Group_2 = ""
Important_Group_3 = ""

An example list of user groups put into a string is set in primaryGroup. 
The result will look like this Important_Group_1,Important_Group_2
