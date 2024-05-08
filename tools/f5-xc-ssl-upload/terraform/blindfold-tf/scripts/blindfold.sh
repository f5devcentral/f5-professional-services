#!/bin/bash

# This script uses the vescrl utility to return an encrypted Blindfold Secret of a Private Key and a
# Certificate in Base64 format to a Terraform configuration file to create a F5XC Load Balancer.

# Defines input variables from terraform
CERTIFICATE=$1
PRIVATE_KEY=$2

# Make temporary unique filenames to store F5XC public-key and policy-document
XC_PUBLIC_KEY="$(mktemp)"
XC_POLICY_DOCUMENT="$(mktemp)"

# Defines timestamp
TIMESTAMP=`date "+%m-%d-%Y %H:%M:%S"`

# Determines if the certificate and private key are in valid PEM format
EVAL_CERT=$(openssl x509 -noout -modulus -in $CERTIFICATE &>/dev/null && echo "true" || echo "false")
EVAL_KEY=$(openssl rsa -noout -modulus -in $PRIVATE_KEY &>/dev/null && echo "true" || echo "false")

if $EVAL_CERT -eq "true" && $EVAL_KEY -eq "true"; then

    # Calculates the md5 checksums of certificate and private key modulus 
    MD5_CERT=$(openssl x509 -noout -modulus -in $CERTIFICATE | openssl md5)
    MD5_KEY=$(openssl rsa -noout -modulus -in $PRIVATE_KEY | openssl md5)

	if [[ "$MD5_CERT" == "$MD5_KEY" ]]; then # Verify if the Private Key matches the Certificate
        	# Obtain the F5XC public-key and stores the output to a temporary file
		vesctl --config ./scripts/.vesconfig request secrets get-public-key > $XC_PUBLIC_KEY

		# Obtain the policy-document and stores the output to a temporary file.
		vesctl --config ./scripts/.vesconfig request secrets get-policy-document --namespace shared --name ves-io-allow-volterra > $XC_POLICY_DOCUMENT

		# Obtains the path of the temporary file
		XC_PUBLIC_KEY_PATH=$(realpath ${XC_PUBLIC_KEY})
        	XC_POLICY_DOCUMENT_PATH=$(realpath ${XC_POLICY_DOCUMENT})

        	# Make temporary unique filenames to store the encrypted blindfold secret of the private key and the certificate in Base64 format
		KEY_BLINDFOLD_SECRET="$(mktemp)"
        	BASE64_CERTIFICATE="$(mktemp)"

		# Encrypt TLS Private Key Using Blindfold
        	vesctl --config ./scripts/.vesconfig request secrets encrypt --policy-document ${XC_POLICY_DOCUMENT_PATH} --public-key ${XC_PUBLIC_KEY_PATH} ${PRIVATE_KEY} > $KEY_BLINDFOLD_SECRET

        	# Check platform Encode the certificate with Base64
		if [ "$(uname)" == "Linux" ]; then
		cat ${CERTIFICATE} | base64 -w0 | awk '{print "string:///"$1}' > $BASE64_CERTIFICATE
		elif [ "$(uname)" == "Darwin" ]; then
		cat ${CERTIFICATE} | base64 | awk '{print "string:///"$1}' > $BASE64_CERTIFICATE
		else
    		echo "Unsupported operating system."
    		exit 1
		fi


        	# Save the Base64 Certificate and Private Key blindfold secret to an array and return it to terraform
		OUTPUT=({\"cert\" : \"$(cat $BASE64_CERTIFICATE)\"", \"blindfold\" : \""$(echo -e "string:///$(cat $KEY_BLINDFOLD_SECRET | tail -n +2)")\"})
        	echo -e ${OUTPUT[@]}
	else
        	# Write a message to stderr if the certificate and private key does not match.
		echo "$TIMESTAMP Invalid TLS certificate and/or Private key: tls: private key does not match public key" >&2
        exit 1
    fi
else
        if [[ "$EVAL_CERT" == "false" ]]; then
		# Write a message to stderr if the certificate is not in valid PEM format
            	echo "$TIMESTAMP Could not read PEM certificate from $CERTIFICATE" >&2
		exit 1
        else
            	# Write a message to stderr if the private key is not in valid PEM format
		echo "$TIMESTAMP Could not read PEM private key from $PRIVATE_KEY" >&2
		exit 1
	fi
fi

