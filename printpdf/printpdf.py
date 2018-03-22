from PyPDF2 import PdfFileReader, PdfFileWriter
import os
import argparse

STYLE_ONE_PER_PAGE = 0
STYLE_TWO_PER_PAGE = 1


def order_for_printer(count, style):
    if style == STYLE_ONE_PER_PAGE:
        all_count = count if count % 2 == 0 else count + 1
        for i in range(0, all_count, 2):
            yield i
        if all_count != count:
            yield -1
        yield -2
        for i in range(all_count - 1, 0, -2):
            yield i

    elif style == STYLE_TWO_PER_PAGE:
        all_count = (count + 3) >> 2 << 2
        for i in range(0, all_count >> 1, 2):
            j = all_count - i - 1
            yield j if j < count else -1
            yield i
        yield -2
        for i in range((all_count >> 1) - 1, 0, -2):
            yield i
            j = all_count - i - 1
            yield j if j < count else -1


def convert_to_printable_pdf(in_name, style):
    _fname, ext = os.path.splitext(in_name)
    outname1 = _fname + '_printable1' + ext
    outname2 = _fname + '_printable2' + ext
    with open(in_name, 'rb') as fin, open(outname1, 'wb') as fout1, open(outname2, 'wb') as fout2:
        pdfin = PdfFileReader(fin)
        pdfout = PdfFileWriter()

        count = pdfin.getNumPages()
        for page in order_for_printer(count, style):
            if page == -1:
                pdfout.addBlankPage()
            elif page == -2:
                pdfout.write(fout1)
                del pdfout
                pdfout = PdfFileWriter()
            else:
                pdfout.addPage(pdfin.getPage(page))

        pdfout.write(fout2)


def main():
    parser = argparse.ArgumentParser(
        description='Convert PDF to 2 printabled pdf')
    parser.add_argument('pdfname', type=str,
                        help='pdf file name to be converted')
    parser.add_argument('--style', choices=['single', 'double'],
                        default='single', help='print style')

    args = parser.parse_args()
    style_map = {
        'single': STYLE_ONE_PER_PAGE,
        'double': STYLE_TWO_PER_PAGE,
    }
    convert_to_printable_pdf(args.pdfname, style_map[args.style])
    print('done')


if __name__ == '__main__':
    main()
