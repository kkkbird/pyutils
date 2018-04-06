# Creator for confd

This convert a common file to confd files

## HOW TO USE

```shell
usage: creator.py [-h] [-i INPUTPATTERN] [-o OUTDIR] [-p PREFIX] [-b BACKEND]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTPATTERN, --inputpattern INPUTPATTERN
                        input file pattern
  -o OUTDIR, --outdir OUTDIR
                        Path for output confd dir
  -p PREFIX, --prefix PREFIX
                        Prefix for confd key
  -b BACKEND, --backend BACKEND
                        backend type for confd output
```

## Example

``` shell
python3 .\creator.py --prefix="/myapp/test"
```
