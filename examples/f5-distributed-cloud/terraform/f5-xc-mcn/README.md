# F5 Distributed Cloud Multi-Cloud deployment

## It creates following
- AWS, Azure and GCP site
- Virtual Network
- Site mesh group (IPSec tunnels)
- it uses 'count' feature to create multiple sites

## Usage:
- configure main.tf as required
- configure backend.tf
- pass your cloud credentials to TF_VARs
