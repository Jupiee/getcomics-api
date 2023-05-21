# Unofficial Getcomics API (v1.3.0)
Unofficial API for getcomics.org using Beautifulsoup scraper and Fast API
<br>

## Features

- Search for comics by title or keywords
- Get the latest comics
- Retrieve detailed metadata for each comic, including title, year, cover image, size, and description

## Error Codes

This is the list of error codes
| Code | Description |
| ------------- | ------------- |
| 200 | OK |
| 201 | Articles not found |
| 202 | Invalid page number |

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/Jupiee/getcomics-api.git
    ```
2. Install required dependencies:

   ```shell
   pip install -r requirements.txt
   ```
## Usage
1. First create a .env file and fill it with your mongodb database URI:

   ```shell
   MONGO_URI= YOUR_MONGODB_URI
   ```
2. Run the main.py file

## Status

see the status for the API here: https://jupieterxyz.betteruptime.com

## Documentation

see the documentation for the API here: https://getcomics-api-production.up.railway.app/docs

## Contributing

Contributions to this project are welcome! If you find any bugs or have suggestions for new features, please open an issue or submit a pull request.

## License

[MIT License](LICENSE)