# TransferErrors

## Use

```bash
$ source ./setup.sh
$ cd bin/
$ python run.py      # does all the API calls and puts stuff in stuck.pkl
$ python write.py    # parses stuck.pkl into a HTML table
```

## python module

The back-end is inside `TransferErrors`. 

`common.py` just contains some class definitions and common variables

`get.py` contains the PhEDEx API calls and stores the output as JSON files

`parse.py` contains functions to parse the JSONs and produce useful data

`display.py` takes the data and produces a simple HTML table

## Executables

These are contained in `bin`

## HTML templates

HTML, CSS, Javascript templates are all in `html`

## Output

The output is in `www`