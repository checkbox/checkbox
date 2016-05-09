#!/bin/bash
new_path=`pwd`
PATH="$PATH":"$new_path"

alg_primary_obj=0x000B
alg_primary_key=0x0001
alg_create_obj=0x000B
alg_create_key=0x0008
halg=0x000B

handle_hmac_key=0x81010013

file_primary_key_ctx=context.p_"$alg_primary_obj"_"$alg_primary_key"
file_hmac_key_pub=opu_"$alg_create_obj"_"$alg_create_key"
file_hmac_key_priv=opr_"$alg_create_obj"_"$alg_create_key"
file_hmac_key_name=name.load_"$alg_primary_obj"_"$alg_primary_key"-"$alg_create_obj"_"$alg_create_key"
file_hmac_key_ctx=ctx_load_out_"$alg_primary_obj"_"$alg_primary_key"-"$alg_create_obj"_"$alg_create_key"
file_hmac_output=hmac_"$file_hmac_key_ctx"

file_input_data=secret.data

fail()
{
	    echo "$1 test fail, please check the environment or parameters!"
        exit 1
}
Pass()
{
	    echo ""$1" pass" >>test_getpubak_pass.log
}

rm $file_primary_key_ctx $file_hmac_key_pub $file_hmac_key_priv $file_hmac_key_name $file_hmac_key_ctx  $file_hmac_output  -rf

if [ ! -e "$file_input_data" ]   
  then    
echo "12345678" > $file_input_data
fi 

tpm2_takeownership -c

tpm2_createprimary -A e -g $alg_primary_obj -G $alg_primary_key -C $file_primary_key_ctx
if [ $? != 0 ];then
	 fail createprimary 
fi
tpm2_create -g $alg_create_obj -G $alg_create_key -o $file_hmac_key_pub -O $file_hmac_key_priv  -c $file_primary_key_ctx
if [ $? != 0 ];then
	fail create 
fi

tpm2_load -c $file_primary_key_ctx  -u $file_hmac_key_pub  -r $file_hmac_key_priv -n $file_hmac_key_name -C $file_hmac_key_ctx
if [ $? != 0 ];then
	fail load   
fi

tpm2_hmac  -c $file_hmac_key_ctx  -g $halg -I $file_input_data -o $file_hmac_output 
if [ $? != 0 ];then
	fail hmac 
fi

####handle test
rm -f $file_hmac_output  
tpm2_evictcontrol -A o -c $file_hmac_key_ctx -S $handle_hmac_key |tee evict.log
c1="$?"
grep "persistentHanlde: "$handle_hmac_key"" evict.log
c2="$?"

if [ $c1 != 0 ] || [ $c2 != 0  ];then
     fail evict
fi

tpm2_hmac  -k $handle_hmac_key  -g $halg -I $file_input_data -o $file_hmac_output 
if [ $? != 0 ];then
	fail hmac 
fi
