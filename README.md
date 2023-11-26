# Million Verifier Python Client
Python client for [Million Verifier](https://www.millionverifier.com/). API documentation can be found 
[here](https://developer.millionverifier.com/#section/Authentication).

# Setup
It is advised that `million-verifier-client` is installed within a virtual environment 
(e.g., [Poetry](https://python-poetry.org/docs/), [venv](https://docs.python.org/3/tutorial/venv.html), etc.). 
Once in an activated virtual environment, `million-verifier-client` can be installed with the following commands:
#### Pip:
```shell
pip install million-verifier-client
```
#### Poetry:
```shell
poetry add million-verifier-client
```

## Example Usage
```python
import os
from million_verifier import MillionVerifierClient

client = MillionVerifierClient(
    api_key=os.getenv("MILLION_VERIFIER_API_KEY"),
)

client.list_files()
```
Output:
```json
{
  "files": [
    {
      "file_id": 25645547490,
      "file_name": "test-emails-1.txt",
      "status": "finished",
      "unique_emails": 0,
      "updated_at": "2023-11-25 12:12:21",
      "createdate": "2023-11-25 12:12:16",
      "percent": 100,
      "total_rows": 10,
      "verified": 9,
      "unverified": 1,
      "ok": 8,
      "catch_all": 0,
      "disposable": 0,
      "invalid": 1,
      "unknown": 0,
      "reverify": 0,
      "credit": 10,
      "estimated_time_sec": 0,
      "error": ""
    }
  ], 
  "total": 1
}
```
# Development
## Testing
Tests can be run using [Pytest](https://docs.pytest.org/en/7.4.x/):
```shell
pytest
```
Or, using Pytest within a Poetry environment:
```shell
poetry run pytest
```
