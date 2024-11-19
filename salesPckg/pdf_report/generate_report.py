import sys
sys.path.append("...")


from fpdf import FPDF
from pathlib import Path
import os, pytz
from datetime import datetime
from dataClasses import SalesDataSource
from create_plots import CreatePlots
import pandas as pd
from appLogger import AppLogger

class GenerateReport:
    def __init__(self, filename : str, logs_file : os.path,  WIDTH : int=210, HEIGHT : int=297):
        self.pdf = FPDF()
        reports_dir = str(Path(os.path.join("salesPckg", "pdf_report", "reports")).resolve())
        os.makedirs(reports_dir, exist_ok=True)
        self.filename = os.path.join(reports_dir, filename)
        self.logs_file = logs_file
        self.logger = AppLogger()
        self.plots = CreatePlots(self.logs_file)
        self.WIDTH = WIDTH 
        self.HEIGHT = HEIGHT
    @property
    def logo_path(self) -> str:
        logo_path = str(Path(os.path.join("static", 'bhvnLogo.png')).resolve().absolute())
        return logo_path
    
    @property
    def plots_path(self) -> str:
        plots_path = Path(os.path.join("salesPckg", "pdf_report", "Plots")).resolve()
        os.makedirs(plots_path, exist_ok=True)
        return plots_path.absolute()

    @property
    def last_week_sales_path(self) -> os.path:
        return os.path.join(self.plots_path, "last_week_sales_plots")
    
    @property
    def current_month_plots_path(self) -> os.path:
        return os.path.join(self.plots_path, "current_month_plots")

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
        self.pdf.write(5, f"Sales Report")
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
            #self.pdf.cell(w = w, h = h, txt = '', ln= 0,
            #align = 'C', fill = False)
            self.pdf.cell(w =50, h = 8, txt = str(summary[0]), border=0,
            align = 'C', fill = False)
            self.pdf.set_text_color(0, 0, 139)
            self.pdf.cell(w = 50, h = 8, txt = str(summary[1]), border=0,
            align = 'C', fill = False)
            if counter % 2==0:
                self.pdf.ln(10)
            counter += 1
        
    def first_page(self):
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Started Writing first page of report...')
        self._add_logo(y=5)
        self._create_title()
        self.lw_sales = self.plots.last_week_sales()
        list_of_invoices = self.lw_sales['custumInvoiceNo'].unique().tolist()
        self.pdf.set_font('Arial', '', 16)
        self.pdf.set_text_color(0, 0, 255)
        self.pdf.write(30, "Recent Invoice Summary")

        for invoice in list_of_invoices:
            self.pdf.set_font('Arial', '', 12)
            self.pdf.set_text_color(255, 0, 0)
            self.pdf.ln(20)
            self.pdf.write(2, f"Invoice # {invoice}")
            invoice_df = self.lw_sales[self.lw_sales['custumInvoiceNo'] == invoice ]
        #(self.total_active, self.present, self.absent, self.maternity, self.beforeMaternity, self.afterMaternity, self.lwd_department, self.lwd_position) = self.plots.attendance_today()
            summary_zip = zip(['Customer PO' ,'BHVN PO:','Customer:', 'Due Date:', 'Invoice Date:', 'Ship Date:', 'Target Leadtime:', 'Actual Leadtime:', 'Delay Days', 'HOT'],
                            [invoice_df['custponumber'].unique()[0], invoice_df['ProductionNo'].unique()[0], invoice_df['custname'].unique()[0], pd.to_datetime(invoice_df['duedate'].unique()[0]).strftime('%d %b, %Y'),
                            pd.to_datetime(invoice_df['invoicedate'].unique()[0]).strftime('%d %b, %Y'), pd.to_datetime(invoice_df['shipdate'].unique()[0]).strftime('%d %b, %Y'),
                            str(int(invoice_df['target_lead_time'].mean()))+" days",str(int(invoice_df['actual_lead_time'].mean()))+" days", 
                            str(int(invoice_df['delay_days'].mean()))+" days", str(int(invoice_df['HOT'].mean()))+" %"])
            self._write_summary(summary_zip, w=3)
            self.pdf.image(os.path.join(self.last_week_sales_path, f"sales_last_week_visuals_{invoice}.png"), y = 110 , x = 5, h = 110 , w=self.WIDTH-40)
            self.pdf.image(os.path.join(self.last_week_sales_path, f"shipment_ratio_{invoice}.png"), y = 110+100 , x = 5, h = 85, w=self.WIDTH-100)
    
    def _get_summary_table(self, df: pd.DataFrame, groupby: str) -> pd.DataFrame: 
        df = df.groupby(groupby, as_index=False).agg('sum')
        df = df.describe(include='all').T
        df = df.reset_index()
        df = df.rename(columns={'25%' : 'Q1', '50%' : 'Q2', '75%' : 'Q3'})
        return df

    def second_page(self):
        self._add_logo( x = self.WIDTH-15, y = 3,  w = 13, h = 13)
        self.current_month_sales = self.plots.current_month_sales()
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Started Writing second page of report...')
        self.pdf.set_text_color(0, 0, 255)
        self.pdf.set_font('Arial', '', 18)
        self.pdf.write(2, f"Current Month Sales Status {self.plots.current_month_name_vn, int(self.current_year_vn)}")
        print(self.current_month_sales.columns.to_list())
        summary_zip = zip(['Invoices Generated :', 'POs Shipped :','Sales Qty:','Sales Value:','Target Leadtime:',
                         'Actual Leadtime:','Avg Delay Days:', 'Avg of %HOT:'],
                        [self.current_month_sales['custumInvoiceNo'].nunique(), self.current_month_sales['custponumber'].nunique(), str(int(self.current_month_sales['Shipped Qty'].sum()))+" pairs", "$ "+str(int(self.current_month_sales['Price(USD)'].sum())), str(int(self.current_month_sales['Target Lead-time'].mean()))+" days",
                        str(int(self.current_month_sales['Actual Lead-time'].mean()))+" days", str(int(self.current_month_sales['Delay (Days)'].mean()))+" days",  str(int(self.current_month_sales['HOT'].mean()))+" %"])

        self._write_summary(summary_zip, w=3)
        
        self.pdf.image(os.path.join(self.current_month_plots_path, "customer_wise_order_qty_ratio.png"), 5, 70, self.WIDTH/2, h=75)
        self.pdf.image(os.path.join(self.current_month_plots_path, "customer_wise_revenue_ratio.png"), self.WIDTH/2, 70, self.WIDTH/2, h=75)
        #self.pdf.image(os.path.join(self.att_today_visuals_path, "designation_wise_att.png"), 5, 10, w = self.WIDTH-20, h = 140)
        self.pdf.image(os.path.join(self.current_month_plots_path, "customer_wise_target_and_actual_leadtime.png"), 5, 145, self.WIDTH/2, h=75)
        self.pdf.image(os.path.join(self.current_month_plots_path, "customer_wise_hot.png"), self.WIDTH/2, 145, self.WIDTH/2, h=75)

        self.pdf.image(os.path.join(self.current_month_plots_path, "pareto_qty.png"), 5, 220, self.WIDTH/2, h=75)
        self.pdf.image(os.path.join(self.current_month_plots_path, "pareto_revenue.png"), self.WIDTH/2, 220, self.WIDTH/2, h=75)
    
    def third_page(self):
        #self.pdf.add_page()
        self._add_logo( x = self.WIDTH-15, y = 3,  w = 13, h = 13)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Started Writing third page of report...')
        self.sales_data = self.plots.operational_kpi()
        self.pdf.set_text_color(0, 0, 255)
        self.pdf.set_font('Arial', '', 20)
        self.pdf.write(5, f"Operational KPIs - {self.current_year_vn}")
        self.pdf.ln(10)
        summary_zip = zip(['Sales Qty:','Sales Value:','Target Leadtime:',
                         'Actual Leadtime:','Avg Delay Days:', 'Avg of %HOT:'],
                        [str(int(self.sales_data['Shipped Qty'].sum()))+" pairs", "$ "+str(int(self.sales_data['Price(USD)'].sum())), str(int(self.sales_data['Target Lead-time'].mean()))+" days",
                        str(int(self.sales_data['Actual Lead-time'].mean()))+" days", str(int(self.sales_data['Delay (Days)'].mean()))+" days",  str(int(self.sales_data['HOT'].mean()))+" %"])

        self._write_summary(summary_zip, w=3)
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_sales_qty.png"), 5, 60, self.WIDTH/2, h=80)
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_sales_value.png"), self.WIDTH/2, 60, self.WIDTH/2, h=80)
        
        self.pdf.image(os.path.join(self.ops_visuals_path, "customer_wise_order_qty_ratio.png"), 5, 140, self.WIDTH/2, h=80)
        self.pdf.image(os.path.join(self.ops_visuals_path, "customer_wise_revenue_ratio.png"), self.WIDTH/2, 140, self.WIDTH/2, h=80)
        
        self.pdf.image(os.path.join(self.ops_visuals_path, "month_wise_avg_order_delay.png"), 5, 210, self.WIDTH/2, h=80)
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_hot.png"), self.WIDTH/2, 210, self.WIDTH/2, h=80)

    def fourth_page(self):
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Started Writing fourth page of report...')
        self._add_logo(x = self.WIDTH-15, y = 3, w = 13, h = 13)
        
        self.pdf.image(os.path.join(self.ops_visuals_path, "customer_wise_target_and_actual_leadtime.png"), 5, 20, self.WIDTH/2, h=90)
        self.pdf.image(os.path.join(self.ops_visuals_path, "monthly_booking_confirmation_time.png"), self.WIDTH/2, 20, self.WIDTH/2, h=90)

        self.pdf.image(os.path.join(self.ops_visuals_path, f"pareto_revenue.png"), y = 120 , x = 5, h = 130 , w=self.WIDTH-5)

    def fifth_page(self):
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Started Writing fifth page of report...')
        self._add_logo(x = self.WIDTH-15, y = 3, w = 13, h = 13)
        self.pdf.image(os.path.join(self.ops_visuals_path, f"pareto_qty.png"), y = 20 , x = 5, h = 120 , w=self.WIDTH-10)
    
    def footer(self):
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(128,0,128)
        self.pdf.ln(140)
        self.pdf.cell(self.WIDTH-5, 10, "For interactive Dashboards, please visit => https://bhvn.ml", align='L')
        self.pdf.set_text_color(0,0, 255)
        self.pdf.ln(10)
        self.pdf.set_font('Arial', '', 7)
        self.pdf.cell(self.WIDTH-5, 10, "Copyright 2022 © Blue Horizon Vietnam", align='L')
        

    def complete_report(self):
        self.first_page()
        self.second_page()
        self.third_page()
        self.fourth_page()
        self.fifth_page()
        self.footer()
        self.pdf.output(self.filename, 'F')
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Sales Report has been generated and successfully saved locally')
        
