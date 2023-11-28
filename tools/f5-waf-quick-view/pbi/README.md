# Requeriments

Microsoft Power BI version 2.123

This Power Bi file creates a dashboard to identify signatures not enforced:

* On File Types
* On URLs
* On Parameters
* On cookies

This is not a solution supported by F5, it was created only to identify easily the policies that need attention.

# HOW IT WORKS

* This application creates a dashboard showing all AWAF(ASM) Security policies that you collected from different BIG-IPs clusters.
  If the AWAF(ASM) is in a cluster you need to add to the device.txt file only the IP of the Active device.
  ![Alt text](3-dashboard.png?raw=true "Signatures-dashboard")
* On the top of the dashboard you will be able to see the total number of policies that you have and It will show the number of good policies.
  Good policies mean that your policy is in blocking mode, and no signatures are in Staging on URLs, Parameters, Cookies, and File Types.
  
  The table creates statistics with the top 10 policies that need more intervention, in other words, that offer more risk to your environment
  This grade is related to the signatures only and it does not verify other items on BIG-IP.
  This grade is made based on the total number of signatures enabled. That means it is not an accurate measure.
  It was created only to give directions on improving the security of AWAF security policies.
  ![Alt text](top.png?raw=true "All Policies Statistics")
  
* On the second bottom half screen you can select the device that you want to verify and the security policies that you want to see. This will
  show a Bar graphic with the number of signatures that are  in Staging mode, Signatures disabled (manually), and signatures with the Block mode disabled
  and the number of signatures that are Ready to be enforced.
  ![Alt text](botton.png?raw=true "Policy per device")

* The Numbers on URLs, Parameters, Cookies, and File Types represent the number of the Items that are on staging. The recommendation for this number is always to be Zero.
  On the CSV file, you can see all Parameters, URLs, Cookies, and File Types names that are in staging.

# HOW TO USE

1. Install Microsoft Power BI on your computer

2. After installing the Power BI open the PBI-F5-WAF-Quick-View.pbix file

3. On Menu home there is an icon called Transform data, click on the Arrow down and choose Data Source Settings
   ![Alt text](01-Transform-data.png?raw=true "Configuring sources")

5. Select the option Data Source in the current file, then click on Change Source and select the CSV file that the f5-awaf-quick view generated on the data directory.
   ![Alt text](02-select-data.png?raw=true "Select the file inside data directory")
   ![Alt text](03-select-data.png?raw=true "Select the file inside data directory")
   
7. Click on Close and Apply changes.
   ![Alt text](05-apply.png?raw=true "Apply configuration")

9. Select the device to update the policies list and select one policy to see the graphics.
   ![Alt text](Dashboard-exp.png?raw=true "Select the file inside data directory")
Enjoy it!


 
