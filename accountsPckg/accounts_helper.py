import pandas as pd 

def preprocess_salaries(df, month, year):
    salaries = pd.read_excel(df, engine="openpyxl", header=1)
    salaries = salaries[['Code\nSố thẻ','Full Name\nHọ và tên', 'Joining Day\nNgày vào','Designation\nChức vụ', 'Position\nBộ Phận', 'Total of workdays\nTổng ngày công','OT Hours\nGiờ tăng ca',
                        'OT Salary\nLương OT','Leave Encashment\nTiền PN','Adwance/ Deduction\nTạm ứng/ Khấu trừ khác', 'Insurance\nBảo hiểm',
                        'Net  Salary\nThực nhận','Gross income\nTổng thu nhập','Total after deduct PIT\nThực nhận']]
    salaries = salaries.dropna(subset=['Code\nSố thẻ'])
    salaries = salaries[(salaries['Code\nSố thẻ'] != 'Prepared By:-') & (salaries['Code\nSố thẻ'] != 2) ]
    salaries = pd.DataFrame(salaries.values, columns=["EmployeeCode","Name", "JoiningDate", "Designation", "Position", "WorkDays", "otHours", "otSalary", "LeaveEncashment","Advance",
                                        "Insurance","NetSalary", "GrossIncome", "TotalAfterDeductPIT"])
    num_cols = ["WorkDays", "otHours", "otSalary", "LeaveEncashment","Advance",
                "Insurance","NetSalary", "GrossIncome", "TotalAfterDeductPIT"]
    cat_cols = ["EmployeeCode","Name","Designation", "Position"]
    salaries[num_cols] = salaries[num_cols].astype(float)
    salaries[cat_cols] = salaries[cat_cols].astype(object)
    salaries['month_year'] = str(month)+str(year)
    return salaries