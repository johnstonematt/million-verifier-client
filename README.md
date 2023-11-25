# Million Verifier Python Client
Python client for [Million Verifier](https://www.millionverifier.com/). API documentation can be found 
[here](https://developer.millionverifier.com/#section/Authentication).

# Example Usage
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
