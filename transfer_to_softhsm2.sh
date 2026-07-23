#!/bin/bash

readonly KEYSTORE_DIR="$HOME/sros2/keystore"
# generate new security officer pin for this project
# should let prompt user for so pin in future
readonly SO_PIN=$(openssl rand -hex 16)

declare -A pin_array

# enable recursive file searching
shopt -s globstar
# prevent errors if no files match
shopt -s nullglob

echo "Generating SoftHSM2 tokens and importing key.pem files in $KEYSTORE_DIR:"
echo

# recursively search for all key.pem files
for file in "$KEYSTORE_DIR"/**/key.pem; do
	enclave_name="${file#"$KEYSTORE_DIR"/}"
	enclave_name="${enclave_name#"enclaves"/}"
	enclave_name="${enclave_name%/key.pem}"
	echo "  Found enclave $enclave_name."

	enclave_name="${enclave_name##*/}"
	echo "	Generating token with name $enclave_name."

	# generate random 16 digit hex pin
	pin=$(openssl rand -hex 16)
	# generate softHSM tokens
	softhsm2-util --init-token --free --label $enclave_name --pin $pin --so-pin $SO_PIN 2>&1 | sed 's/^/\t/'
	# import sros2 key into softHSM tokens
	softhsm2-util --import "$file" --token $enclave_name --label key --pin $pin --id 123456789ABCDEF123456789ABCDEF 2>&1 | sed 's/^/\t/'
	echo

	# remove sros2 key after importing
	rm "$file"
	# extract PKCS #11 URIs and save to key.p11 file
	GNUTLS_PIN=$pin p11tool --provider /opt/softhsm2/lib/softhsm/libsofthsm2.so --list-tokens --login | grep "token=$enclave_name" | awk -v pin=$pin '{print $2 "?pin-value=" pin}' > "${file%.pem}.p11"
	echo "Wrote PKCS #11 URI to key.p11 file."
	
	pin_array["$enclave_name"]="$pin"
done

echo "Done."
echo
echo "Keep generated pins for reference."

# print out newly generate pins
readonly FORMAT="%-50s %-16s\n"
echo "SO pin:" 
printf "$FORMAT" "	" " $SO_PIN"
echo "Pins: "
for enclave in "${!pin_array[@]}"; do
	printf "$FORMAT" "	$enclave:" " ${pin_array[$enclave]}"
done


