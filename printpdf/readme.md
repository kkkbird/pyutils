# PrintPDF

用于双面打印PDF，仅在`HP LaserJet 1022n Class Driver`上测试过

## 使用方式

* 安装python3 & pip install PyPDF2
* 运行printpdf.py

```shell
usage: printpdf.py [-h] [--style {single,double}] pdfname

Convert PDF to 2 printabled pdf

positional arguments:
  pdfname               pdf file name to be converted

optional arguments:
  -h, --help            show this help message and exit
  --style {single,double}
                        print style
```

* 运行后生成\_printable1.pdf和\_printable2为结尾的文件
  * style为`single`时为普通双面打印，打印完成printable1后将打印面朝下正面朝打印机内测打印printable2
  * sytle为`double`时为书页打印模式，打印完成printable1后将打印面朝下第一页方向朝向打印机内测打印printable2
