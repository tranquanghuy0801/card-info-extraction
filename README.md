## Card Info Extraction

# Create virtual environment
```
NAME_ENV = "ocr-card"
virtualenv -p python3 $NAME_ENV
source $NAME_ENV/bin/activate
pip install -r requirements.txt 
```

# Get the dataset
```
chmod +x get_dataset.sh
./get_dataset.sh
```

# Test the result 

<b>Get the test results for a folder of images</b>

Uncomment the last piece of code in file "cloud_ocr/google_vision_main.py"

```
python3 cloud_ocr/google_vision_main.py -i <input_data> -o <output_file> -c <num_choice>

python3 cloud_ocr/google_vision_main.py -i data/train_data -o results/train_data.txt -c 1
```

<b> View accuracy of test results</b>

```
python3 cloud_ocr/test_performance.py -t <test_file> -r <reference_file> -l <file_log>

python3 cloud_ocr/test_performance.py -t results/train_data.txt -r data/train_data/train.txt -l logs/train_data.log
```

![screenshot  of command line](results/screenshot.jpg)

# Run API using Docker

Change <b>from helper import *</b> into <b>from cloud_ocr.helper import *</b>

```
docker-compose build
docker-compose up 
```

# API Documentation

<b> POST Request </b>

```
POST /api/info HTTP/1.1
Content-Type: application/json; charset=utf-8

{
	"data": (url of image),
	"choice": (1: ID cards - 2: Passport)
}
```

<b> Response </b>

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{
	"id": "my_id",
    "name": "my_name",
    "dob": "my_dob"
}
```

<b> Code: 404 - Message (ID, Name or DOB not found) </b>

<b> Example

POST Request (Run POSTMAN or python client.py)
```
{
	"data": "https://d1plicc6iqzi9y.cloudfront.net/sites/default/files/image/201806/25/trinh-thi-oanh_img_0_0.JPEG",
	"choice": 1
}
```

Response
```
{
    "dob": "22/04/1994",
    "id": "174190596",
    "name": "TRINH THI OANH"
}
```

# Python Version (3.6.8)