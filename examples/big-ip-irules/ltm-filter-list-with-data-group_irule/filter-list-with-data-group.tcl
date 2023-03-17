# This iRule will allow you to put a list of important security groups in a Data Group then only list those groups in a string as opposed to a very long string with groups you do not care about.
# String Type Data Group
# /Common/Groupnames
# Important_Group_1 = ""
# Important_Group_2 = ""
# Important_Group_3 = ""
# An example list of user groups put into a string is set in primaryGroup. 
# The result will look like this Important_Group_1,Important_Group_2

when HTTP_REQUEST {
    set primaryGroup "Important_Group_1,aaa,Important_Group_2,bbbb"
    set dg_group_names "/Common/Groupnames"
    set dg_names [class names $dg_group_names]
    set newGroupInfo ""

    foreach index ${dg_names} {
        if { $primaryGroup contains ${index} } {
            append newGroupInfo ${index}
            append newGroupInfo ","
        }
    }
    set newGroupInfo [string trimright $newGroupInfo ","]
    log local0. "List of important groups are: $newGroupInfo"
}
