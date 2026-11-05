# Installation

```bash
pip install pydantic                 # core library
pip install "pydantic[email]"        # adds EmailStr support
pip install pydantic-settings        # settings / env var management
```

Check the version:

```python
import pydantic
print(pydantic.VERSION)
```
