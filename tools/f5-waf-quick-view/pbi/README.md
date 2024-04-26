# Overview
This Power BI file creates a dashboard to easily identify policies that need attention by identifying signatures that need to be enforced on:

* File Types
* URLs
* Parameters
* Cookies

# Requirements
* Microsoft Power BI version 2.123
* One or more F5 BIG-IP Advanced WAF / BIG-IP Application Security Manager quick views (see [f5-awaf-quick-view](https://github.com/f5devcentral/f5-professional-services/tree/main/tools/f5-waf-quick-view))

# How It Works

This application creates a dashboard showing all Advanced WAF and/or Application Security Manager security policies that you collected from different BIG-IPs clusters. On the top of the dashboard you will be able to see the total number of policies that you have and it will show the number of good policies. Good policies mean that your policy is in blocking mode, and no signatures are in staging on URLs, Parameters, Cookies, and File Types.

  ![Alt text](3-dashboard.png?raw=true "Signatures-dashboard")
  
  The table creates statistics with the top 10 policies that need more intervention, in other words, that offer more risk to your environment. This grade is related to the signatures only and it does not verify other items on BIG-IP. This grade is made based on the total number of signatures enabled. That means it is not an accurate measure. It was created only to give directions on improving the security of Advanced WAF security policies.
  
  ![Alt text](top.png?raw=true "All Policies Statistics")
  
On the bottom half of the screen you can select the device that you want to verify and the security policies that you want to see. This will show a bar graph with the number of signatures that are in staging mode, signatures disabled (manually), signatures with block mode disabled, and the number of signatures that are ready to be enforced.

  ![Alt text](botton.png?raw=true "Policy per device")

The numbers under URLs, Parameters, Cookies, and File Types represent the number of the items that are in staging. The recommendation for this number is always to be zero (0). On the CSV file, you can see all Parameters, URLs, Cookies, and File Types names that are in staging.

# Usage

1. First, collect one or more Advanced WAF / ASM quick views using the [f5-awaf-quick-view](https://github.com/f5devcentral/f5-professional-services/tree/main/tools/f5-waf-quick-view) utility.
  
   *Note: If the Advanced WAF (ASM) is in a cluster you only need to collect one quick view from the pair (ex. only add the IP of the active unit to the device.txt file).*

2. Open the PBI-F5-WAF-Quick-View.pbix file in Microsoft Power BI.

3. On the Home menu there is an icon called Transform data, click on the arrow down and choose "Data Source Settings."
   
   ![Alt text](01-Transform-data.png?raw=true "Configuring sources")

5. Select the "Data sources in current file" option, then click on Change Source and select the CSV file that the [f5-awaf-quick-view](https://github.com/f5devcentral/f5-professional-services/tree/main/tools/f5-waf-quick-view) generated on the data directory.
   
   ![Alt text](02-select-data.png?raw=true "Select the file inside data directory")
   ![Alt text](03-select-data.png?raw=true "Select the file inside data directory")
   
7. Click on Close and Apply changes.
   
   ![Alt text](05-apply.png?raw=true "Apply configuration")

9. Select the device to update the policies list and select one policy to see the graphics.
    
   ![Alt text](Dashboard-exp.png?raw=true "Select the file inside data directory")
   
Enjoy it!


 
