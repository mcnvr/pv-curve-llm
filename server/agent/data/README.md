# RAG Training Data

The data in this directory serves to train the RAG agent. It is not yet included in the Git repository pending copyright review.

## TODO

- [ ] Review copyright information/legality for including training resources in Open-Source Git Repo
- [ ] Properly cite training resources under a citations header

## Required Data Format

Each `.txt` document must be separated into chunks by 2 newlines ```\n\n```

Example text document format:
```
This is one chunk of data.

This is another chunk of data.
```

This is automatically embedded into the vector database based on this format.
Run `../train.py` locally to retrain the RAG agent.
