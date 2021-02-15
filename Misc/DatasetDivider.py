import xlrd
from xlwt import Workbook
import numpy as np

input_file = ""
output_file = ""
write_wb = Workbook()
write_sheet = write_wb.add_sheet('Sheet 1')

read_wb = xlrd.open_workbook(input_file)
read_sheet = read_wb.sheet_by_index(0)

output_row = 0
output_col = 0

finish_flag = False

rows = read_sheet.nrows
while not finish_flag:
    np.random.randint(0,rows)

events = {}
#classifications = []
for row in range(read_sheet.nrows):
    cell_text = read_sheet.cell_value(row, 0)
    classification = read_sheet.cell_value(row, 1)

    write_sheet.write(output_row, output_col, cell_text)


write_wb.save(output_file)