import sys
sys.path.append("...")


from fpdf import FPDF
from pathlib import Path
import os, pytz
from datetime import datetime
from dataClasses import HRdataSource
from create_plots import CreatePlots
import pandas as pd
from appLogger import get_logger

class GenerateReport:
    def __init__(self, filename : str, logs_file : os.path,  WIDTH : int=210, HEIGHT : int=297):
        self.pdf = FPDF()
        reports_dir = str(Path(os.path.join("hrPckg", "pdf_report", "reports")).resolve())
        os.makedirs(reports_dir, exist_ok=True)
        self.filename = os.path.join(reports_dir, filename)
        self.logs_file = logs_file
        self.logger = get_logger(self.logs_file)
        self.plots = CreatePlots(self.logs_file)
        self.WIDTH = WIDTH 
        self.HEIGHT = HEIGHT
    @property
    def logo_path(self) -> str:
        logo_path = str(Path(os.path.join("static", 'bhvnLogo.png')).resolve().absolute())
        return logo_path
    
    @property
    def plots_path(self) -> str:
        plots_path = Path(os.path.join("hrPckg", "pdf_report", "Plots")).resolve()
        os.makedirs(plots_path, exist_ok=True)
        return plots_path.absolute()

    @property
    def att_today_visuals_path(self) -> os.path:
        return os.path.join(self.plots_path, "att_today_plots")

    @property
    def ops_visuals_path(self) -> os.path:
        return os.path.join(self.plots_path, "operational_plots")
    @property
    def abs_visuals_path(self) -> os.path:
        return os.path.join(self.plots_path, "absenteeism_plots")
    @property
    def today_vn(self) -> str:
        return datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%d %b, %Y")
    @property
    def current_year_vn(self) -> str:
        return datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y")
    
    def _output_df_to_pdf(self, df, distance_from_top = 10):
        # A cell is a rectangular area, possibly framed, which contains some text
        # Set the width and height of cell
        table_cell_width = 14
        table_cell_height = 5
        # Select a font as Arial, bold, 8
        self.pdf.set_font('Arial', 'B', 8)
        
        # Loop over to print column names
        cols = df.columns
        self.pdf.ln(distance_from_top)
        self.pdf.set_text_color(0, 0, 255)
        for col in cols:
            self.pdf.cell(table_cell_width, table_cell_height, col, align='C', border=1)
        # Line break
        self.pdf.ln(table_cell_height)
        self.pdf.set_font('Arial', '', 6)
        # Loop over to print each data in the table
        self.pdf.set_text_color(128,0,128)
        for row in df.itertuples():
            for col in cols:
                try:
                    value = str(round(getattr(row, col), 2))
                except:
                    value = str(getattr(row, col))
                self.pdf.cell(table_cell_width, table_cell_height, value, align='C', border=1)
            self.pdf.ln(table_cell_height)

    def _add_logo(self, x = None, y = 0,  w = 30, h = 30):
        self.pdf.add_page()
        if x is None:
            x = self.WIDTH-40
        self.pdf.image(self.logo_path, x = x, y = y, w = w, h = h)

    def _create_title(self):
        self.pdf.set_text_color(0, 0, 255)
        self.pdf.set_font('Arial', '', 24)
        self.pdf.write(5, f"Human Resouce Department Report")
        self.pdf.ln(10)
        self.pdf.set_text_color(255, 0, 0)
        self.pdf.set_font('Arial', '', 16)
        self.pdf.write(4, f'{self.today_vn}')
        self.pdf.ln(5)

    def _write_summary(self, summary_zip, w = 20, h = 8):
        self.pdf.ln(10)
        counter = 1
        for summary in summary_zip:
            #if str(summary[0]) in ["Present", 'Absent', 'Maternity']:
            self.pdf.set_text_color(0,128,0)
            self.pdf.cell(w = w, h = h, txt = '', ln= 0,
            align = 'C', fill = False)
            self.pdf.cell(w =40, h = 8, txt = str(summary[0]), border=0,
            align = 'C', fill = False)
            self.pdf.set_text_color(0, 0, 139)
            self.pdf.cell(w = 40, h = 8, txt = str(summary[1]), border=0,
            align = 'C', fill = False)
            if counter % 2==0:
                self.pdf.ln(10)
            counter += 1
        
    def first_page(self):
        self.logger.info('Started Writing first page of report...')
        self._add_logo(y=5)
        self._create_title()
        
        (self.total_active, self.present, self.absent, self.maternity, self.beforeMaternity, self.afterMaternity, self.lwd_department, self.lwd_position) = self.plots.attendance_today()
        summary_zip = zip(['Working:' ,'Present:', 'Absent:', 'Maternity:', 'Before Maternity:', 'After Maternity:'],
                          [self.total_active, self.present, self.absent, self.maternity, self.beforeMaternity, self.afterMaternity])
        self._write_summary(summary_zip, w=3)
        
        self.pdf.image(os.path.join(self.att_today_visuals_path, "dep_wise_att_status.png"), 5, 70, w = self.WIDTH-20, h = 110)
        self.pdf.image(os.path.join(self.att_today_visuals_path, "dep_wise_complete_data.png"), 5, 180, w = self.WIDTH-20, h = 110)

    def _get_summary_table(self, df: pd.DataFrame, groupby: str) -> pd.DataFrame: 
        df = df.groupby(groupby, as_index=False).agg('sum')
        df = df.describe(include='all').T
        df = df.reset_index()
        df = df.rename(columns={'25%' : 'Q1', '50%' : 'Q2', '75%' : 'Q3'})
        return df

    def second_page(self):
        #self.pdf.add_page()
        self.logger.info('Started Writing second page of report...')
        self._add_logo( x = self.WIDTH-15, y = 3,  w = 13, h = 13)
        self.pdf.image(os.path.join(self.att_today_visuals_path, "designation_wise_att.png"), 5, 10, w = self.WIDTH-20, h = 140)
        
        self.pdf.ln(140)
        self.pdf.set_text_color(128,0,128)
        self.pdf.set_font('Arial', '', 18)
        self.pdf.write(5, f"Department Summary Stats")

        dep_summary_tbl = self._get_summary_table(self.lwd_department, "Department")
        self._output_df_to_pdf(dep_summary_tbl, distance_from_top= 10)

        self.pdf.ln(10)
        self.pdf.set_text_color(128,0,128)
        self.pdf.set_font('Arial', '', 18)
        self.pdf.write(5, f"Designation Summary Stats")

        dsig_summary_tbl = self._get_summary_table(self.lwd_position, "Position")
        self._output_df_to_pdf(dsig_summary_tbl, distance_from_top= 10)
        
        
    def third_page(self):
        #self.pdf.add_page()

        self.logger.info('Started Writing third page of report...')
        self.plots.operational_plots()
        self._add_logo(x = self.WIDTH-15, y = 3, w = 13, h = 13)
        self.pdf.set_text_color(0, 0, 255)
        self.pdf.set_font('Arial', '', 20)
        self.pdf.write(5, f"Operational KPIs - {self.current_year_vn}")
        self.pdf.ln(10)
        summary_zip = self.plots.operational_kpis_summary()
        self._write_summary(summary_zip, w=10)
        
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_absenteeism.png"), 5, 70, self.WIDTH/2-5, h=70)
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_turnover.png"), self.WIDTH/2, 70, self.WIDTH/2-5, h=70)

        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_net_hire_ratio.png"), 5, 140, self.WIDTH/2-5 , h =70)
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_hire_rate.png"), self.WIDTH/2, 140, self.WIDTH/2-5, h=70)
        
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_emp_summary.png"), 5, 210, self.WIDTH/2-5 , h =70)
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_emp_status.png"), self.WIDTH/2, 210, self.WIDTH/2-5, h=70)
    def fourth_page(self):
        self.logger.info('Started Writing fourth page of report...')
        self.plots.abs_plots()
        #self.pdf.add_page()
        self._add_logo(x = self.WIDTH-15, y = 3, w = 13, h = 13)
        self.pdf.set_text_color(0, 0, 255)
        self.pdf.set_font('Arial', '', 20)
        self.pdf.write(5, f"Absenteeism Analysis - {self.current_year_vn}")
        
        self.pdf.image(os.path.join(self.abs_visuals_path, "monthly_absenteeism.png"), 5, 20, self.WIDTH/2-5, h=90)
        self.pdf.image(os.path.join(self.abs_visuals_path, "daily_absenteeism.png"), self.WIDTH/2, 20, self.WIDTH/2-5, h=90)

        self.pdf.image(os.path.join(self.abs_visuals_path, "age_group_wise_abs.png"), 5, 110 , self.WIDTH/2-5 , h =90)
        self.pdf.image(os.path.join(self.abs_visuals_path, "age_group_wise_abs_ratio.png"), self.WIDTH/2, 110, self.WIDTH/2-20, h=90)
        
        self.pdf.image(os.path.join(self.abs_visuals_path, "gender_wise_abs.png"), 5, 200, self.WIDTH/2-5 , h =90)
        self.pdf.image(os.path.join(self.abs_visuals_path, "gender_wise_abs_ratio.png"), self.WIDTH/2, 200, self.WIDTH/2-20, h=90)

    def fifth_page(self):
        #self.pdf.add_page()
        self.logger.info('Started Writing fifth page of report...')
        self._add_logo( x = self.WIDTH-15, y = 3,  w = 13, h = 13)
        self.pdf.image(os.path.join(self.abs_visuals_path, "marital_status_wise_abs.png"), 5, 20, self.WIDTH/2-5, h=90)
        self.pdf.image(os.path.join(self.abs_visuals_path, "marital_status_wise_abs_ratio.png"), self.WIDTH/2, 20, self.WIDTH/2-0, h=90)

        self.pdf.image(os.path.join(self.abs_visuals_path, "department_wise_abs.png"), 5, 100, w = self.WIDTH-20, h = 150)
        
    def footer(self):
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(128,0,128)
        self.pdf.ln(240)
        self.pdf.cell(self.WIDTH-5, 10, "For interactive Dashboards, please visit => https://bhvn.ml", align='L')
        self.pdf.set_text_color(0,0, 255)
        self.pdf.ln(10)
        self.pdf.set_font('Arial', '', 7)
        self.pdf.cell(self.WIDTH-5, 10, "Copyright 2022-2023 © Blue Horizon Vietnam", align='L')
        

    def complete_report(self):
        self.first_page()
        self.second_page()
        self.third_page()
        self.fourth_page()
        self.fifth_page()
        self.footer()
        self.pdf.output(self.filename, 'F')
        self.logger.info('HR Report has been generated and successfully saved locally')
        
