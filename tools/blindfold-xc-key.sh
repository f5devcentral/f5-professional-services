echo "This script will blindfold your TLS private key for F5 Distributed Cloud";
echo "";
echo "---------------------------------------------------";
echo "";
echo "Paste your private key:"
IFS= read -d '' -n 1 private_key_text 
while IFS= read -d '' -n 1 -t 2 c
do
    private_key_text+=$c
done
echo "$private_key_text" > cert.key;
echo "";
# Get public key
vesctl --cert file:///vescred.cert --key file:///vesprivate.key -u https://f5-consult.console.ves.volterra.io/api request secrets get-public-key > f5-xc-sp-pubkey
 
# Get policy document / secret policy
vesctl --cert file:///vescred.cert --key file:///vesprivate.key -u https://f5-consult.console.ves.volterra.io/api request secrets get-policy-document --namespace shared --name f5-xc-secret-policy > f5-xc-secret-policy

# Encrypt secret and output to screen
echo "";
echo "Here is your blindfolded private key for F5 Distributed Cloud deployment:" 
echo "";
echo "---------------------------------------------------";
# Encrypt secret and output to screen
vesctl --cert file:///vescred.cert --key file:///vesprivate.key -u https://f5-consult.console.ves.volterra.io/api request secrets encrypt --policy-document f5-xc-secret-policy --public-key f5-xc-sp-pubkey cert.key 
echo "";
echo "---------------------------------------------------";
echo "Good Bye";
echo "";

#remove private key
rm cert.key;
