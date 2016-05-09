#!/bin/bash
new_path=`pwd`
PATH="$PATH":"$new_path"

file_primary_key_ctx=context.p_B1
file_rsaencrypt_key_pub=opuB1_B8
file_rsaencrypt_key_priv=oprB1_B8
file_rsaencrypt_key_ctx=context_loadext_out_B1_B8
file_rsadecrypt_key_ctx=context_load_out_B1_B8
file_rsaencrypt_key_name=name.load.B1_B8

file_rsa_en_output_data=rsa_en.out 
file_rsa_de_output_data=rsa_de.out
file_input_data=secret.data 
  
alg_hash=0x000B
alg_primary_key=0x0001
alg_rsaencrypt_key=0x0001

if [ ! -e "$file_input_data" ]   
  then    
echo "12345678" > $file_input_data
fi 
rm $file_primary_key_ctx $file_rsaencrypt_key_pub $file_rsaencrypt_key_priv $file_rsaencrypt_key_ctx $file_rsaencrypt_key_name $file_output_data $file_rsa_en_output_data $file_rsa_de_output_data -rf

tpm2_takeownership -c

tpm2_createprimary -A e -g $alg_hash -G $alg_primary_key -C $file_primary_key_ctx
if [ $? != 0 ];then
echo "createprimary fail, please check the environment or parameters!"
exit 1
fi
tpm2_create -g $alg_hash -G $alg_rsaencrypt_key -o $file_rsaencrypt_key_pub -O $file_rsaencrypt_key_priv  -c $file_primary_key_ctx
if [ $? != 0 ];then
echo "create fail, please check the environment or parameters!"
exit 1
fi
tpm2_loadexternal -H n   -u $file_rsaencrypt_key_pub  -C $file_rsaencrypt_key_ctx
if [ $? != 0 ];then
echo "loadexternal fail, please check the environment or parameters!"
exit 1
fi
tpm2_rsaencrypt -c $file_rsaencrypt_key_ctx -I $file_input_data -o $file_rsa_en_output_data 
if [ $? != 0 ];then
echo "rsa encrypt fail, please check the environment or parameters!"
exit 1
fi

tpm2_load -c $file_primary_key_ctx -u $file_rsaencrypt_key_pub -r $file_rsaencrypt_key_priv  -n $file_rsaencrypt_key_name  -C $file_rsadecrypt_key_ctx 
if [ $? != 0 ];then
echo "load fail, please check the environment or parameters!"
exit 1
fi

tpm2_rsadecrypt -c $file_rsadecrypt_key_ctx  -I  $file_rsa_en_output_data -o  $file_rsa_de_output_data
if [ $? != 0 ];then
echo "rsa decrypt fail, please check the environment or parameters!"
exit 1
fi
