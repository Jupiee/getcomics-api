[license]: https://github.com/Jupiee/getcomics-api/blob/master/LICENSE
[license-img]: https://img.shields.io/badge/License-MIT-white.svg

[ ![license-img][] ][LICENSE]
# Unofficial Getcomics API (v2.0.2)
Unofficial API for getcomics.org using Selectolax scraper and Fast API
<br>

## Features

- Search for comics by title or keywords
- Get the latest comics
- Search for comics by tag
- Retrieve detailed metadata for each comic, including title, year, cover image, size, and description

## Error Codes

This is the list of error codes
| Code | Description |
| ------------- | ------------- |
| 200 | OK |
| 201 | Articles not found |
| 202 | Invalid page number or Unknown query |

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/Jupiee/getcomics-api.git
    ```
2. Install required dependencies:pip install -r requirements.txt

   ```shell
   pip install -r requirements.txt
   ```
## Usage
1. First create a .env file and fill it with your mongodb database URI:

   ```shell
   URI= YOUR_MONGODB_URI
   ```
2. Run the main.py file

## Docker Usage
1. Build the image:
   ```shell
   docker build -t getcomics-api .
   ```
2. Run the image:
   ```shell
   docker run -p 80:80 getcomics-api
   ```

## Status

see the status for the API here: https://jupieterxyz.betteruptime.com

## Documentation

see the documentation for the API here: https://getcomics-api-production.up.railway.app/docs

## Contributing

Contributions to this project are welcome! If you find any bugs or have suggestions for new features, please open an issue or submit a pull request.

## License

[MIT License](LICENSE)