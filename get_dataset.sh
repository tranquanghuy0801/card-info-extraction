# Get all datasets
if [ ! -f data.zip ]; then
    gdown --id 18Susdmo98OwHmCEqeXh-MgdYXwyar7gy --output data.zip
    unzip data.zip 
    mv data_passport_id/ data/
fi