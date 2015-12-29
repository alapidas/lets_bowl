# RESTful Bowling

## The sauce
Create a virtualenv, activate it, and install reqs
```
mkdir env && . env/bin/activate && pip install -r requirements.txt
```
Run the server
```
make runserver
```
Run tests
```
make test
```

## TODOs:
- Admin/SU login to modify scores/frames after the fact
- The ID gen in the mixin is a hack - a real ORM would probably take care of this
- Limitation - we're only allowing POSTs of full frames.  The current player on their current frame will be in flight until it's posted (as opposed to POSTing individual shots).
- Support multiple configs for runtime
- Right now assume `application/json` for content-types in all communication - should handle missing headers, or alternative formats
- Don't assume all POSTdata is valid
- Make selection of fields to serialize automatic
- Support user-selected fields on responses
- General error/edge case handling
- PUT + DELETE support for model items where it makes sense

## Limitations:
- Everything is in memory - the bowling alley has a robust backup generator, but should that fail, all data will be lost
