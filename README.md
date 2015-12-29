TODOs:
- Do an actual README
- Admin/SU login to modify scores/frames after the fact
- The ID gen in the mixin is a hack - a real ORM would probably take care of this
- Limitation - we're only allowing POSTs of full frames.  The current player on their current frame will be in flight until it's posted (as opposed to POSTing individual shots).
- Support multiple configs for runtime
- Right now assume `application/json` for content-types in all communication.  TODO - Handle missing headers, or alternative formats
- Don't assume all POSTdata is valid
- Make selection of fields to serialize automatic
- Support user-selected fields on responses
- General error/edge case handling
- PUT + DELETE support for model items where it makes sense
- Games ended up not being super testable

Limitations:
- Everything is in memory - the bowling alley has a robust backup generator, but should that fail, all data will be lost
- This bowling alley only stores your most recently played game, and only allows you to be in one game at a time
