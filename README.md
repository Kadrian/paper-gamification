paper-gamification
==================

A tool to help you write a paper.

Paper-gamification is a python script that watches a paper written in text format and calculates text statistics as soon as you hit save.

It currently supports:

- Text or markdown
- PDF
- Docx (Microsoft Word)

## Dependencies

```pip install -r requirements.txt```

Will automatically install the following:

- Requests - http://docs.python-requests.org/en/latest/
- Watchdog - http://pythonhosted.org/watchdog/
- Latex support - https://github.com/euske/pdfminer/
- Docx Parser - https://github.com/python-openxml/python-docx
- Natural Language Toolkit (NLTK) - http://www.nltk.org/

Then, use the nltk download tool to load the corpus `wordnet`:

```
import nltk
nltk.download()
```

## Usage

```python tracker.py <paper-file> <publish-host> <paper-id>```

* `<paper-file>` - Source of your paper
* `<publish-host>` - Root url of your deployed [paper-gamification-website](https://github.com/Kadrian/paper-gamification-website "Repo of the corresponding website") (Avoid a trailing '/')
* `<paper-id>` - The database id of your paper in the paper-gamification-website (hacky :D)

## Example

```python tracker.py /usr/path/to/my-paper.md http://localhost:3000 5```

## Contribution

Please feel free to contribute! I'm rather new to open source publishing ;)
