import sys
sys.path.append("...")
from dataClasses import SalesDataSource
from loader import LoadData
import pandas as pd
import datetime, pytz, os, calendar
#from hrPckg import hr_helper
from vizpool.interactive import EDA
from pathlib import Path
from appLogger import AppLogger

class CreatePlots:
    def __init__(self, logs_file: os.path, load_data: bool=True):
        if load_data:
            self.dl = LoadData()
        self.logs_file = logs_file
        self.logger = AppLogger()

        self.sales_last_week_visuals = os.path.join(self.visuals_dir, "last_week_sales_plots")
        os.makedirs(self.sales_last_week_visuals, exist_ok=True)

        self.operational_plots = os.path.join(self.visuals_dir, "operational_plots")
        os.makedirs(self.operational_plots, exist_ok=True)

        self.current_month_plots = os.path.join(self.visuals_dir, "current_month_plots")
        os.makedirs(self.current_month_plots, exist_ok=True)

    def get_sales_data(self, dates: list[pd.Timestamp] = None, year: list[int] = None):
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Getting Sales data executing "get_sales_data" method of "CreatePlots" class')
        sales_data = SalesDataSource(self.dl.sales_data)
        self.sales_data = sales_data.preprocess_data(dates, year)
        
    @property
    def today_vn(self) -> str:
        return datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%d %b, %Y")

    @property
    def last_week_dates(self) -> list[pd.Timestamp]:
        return pd.date_range(end=self.today_vn, periods=15).tolist()

    @property
    def datelist_today(self) -> list[pd.Timestamp]:
        return pd.date_range(end=self.today_vn, periods=1).tolist()

    @property
    def current_year_vn(self) -> int:
        return int(datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y"))
    
    @property
    def visuals_dir(self) -> str:
        #path = Path("generate_plots.py")
        #complete_path = path.resolve()
        visuals_dir = os.path.join(str(Path(os.path.join("salesPckg", "pdf_report")).resolve().absolute()), 'Plots')
        os.makedirs(visuals_dir, exist_ok=True)
        return visuals_dir
    
    def get_dates_list(self, sdate: pd.Timestamp, edate: pd.Timestamp) -> list[pd.Timestamp]:
        return pd.date_range(sdate, edate ,freq='d')
    
    @property
    def current_month_vn(self) -> int:
        return datetime.datetime.now(pytz.timezone("Asia/Jakarta")).month
    
    @property
    def current_month_name_vn(self) -> str:
        return calendar.month_name[self.current_month_vn]

    @property
    def current_month_dates_vn(self) -> list[pd.Timestamp]:
        year = self.current_year_vn
        month = self.current_month_vn
        num_days = calendar.monthrange(year, month)[1]
        return [datetime.date(year, month, day) for day in range(1, num_days+1)]

    def last_week_sales(self):
        '''Current Implementation of this function returns the recent sale invoice''' 
        self.get_sales_data(dates = self.last_week_dates)
        self.sales_data = self.sales_data[self.sales_data['invoicedate'] == max(self.sales_data['invoicedate'])]
        print(self.sales_data['custumInvoiceNo'].nunique())
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Creating "Recent Invoice" plots, executing "last_week_sales" method of "CreatePlots" class ...')
        
        if len(self.sales_data) == 0:
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f'!!!!! Returning "None" for "last_week_sales" as there no invoices generated in last week !!!!!')
                return None

        self.list_of_invoices = self.sales_data['custumInvoiceNo'].unique().tolist()

        for invoice in self.list_of_invoices:
            sales_eda = EDA(self.sales_data[self.sales_data['custumInvoiceNo']==invoice])
            fig = sales_eda.stack_or_group_chart(categories = 'size', aggfunc ='sum', orientation = 'h',
                                            barmode = 'group', values = ['Price(USD)','order_qty','Delayed Qty', 'shipped_qty'], title = 'Size wise Price and Quantity Comparison')

            fig.write_image(os.path.join(self.sales_last_week_visuals, f"sales_last_week_visuals_{invoice}.png"))
            fig = sales_eda.piechart(categories = 'size', values = 'shipped_qty', title = f"Product Shipment Ratio")
            fig.write_image(os.path.join(self.sales_last_week_visuals, f"shipment_ratio_{invoice}.png"))
        
        return self.sales_data

    def current_month_sales(self):
        self.get_sales_data(dates = self.current_month_dates_vn)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, 'Creating "Current Month Sales" plots, executing "current_month_sales" method of "CreatePlots" class ...')
            self.sales_data.rename(columns={'salesmonth': 'Sales Month', 'shipped_qty':'Shipped Qty',
                                'custname': 'Customer', 'target_lead_time': 'Target Lead-time',
                                'actual_lead_time': 'Actual Lead-time', 'delay_days': 'Delay (Days)',
                                'booking_conf_time':'Booking Confirmation Time', 'lotnumber_x': 'Lot Number'}, inplace = True)
            sales_instance = EDA(self.sales_data)
            fig = sales_instance.piechart(categories='Customer', values = 'Price(USD)',  width = 750, height = 600,
                             title = "Customer wise Revenue Ratio")
            fig.write_image(os.path.join(self.current_month_plots, "customer_wise_revenue_ratio.png"))
            fig = sales_instance.piechart(categories='Customer', values = 'Shipped Qty',  width = 750, height = 600,
                             title = "Customer wise Order Qty Ratio")
            fig.write_image(os.path.join(self.current_month_plots, "customer_wise_order_qty_ratio.png"))

            fig = sales_instance.stack_or_group_chart(categories='Customer', values = ['Target Lead-time', 'Actual Lead-time'], unit = "days", orientation ='h',
                    sort_by ='Actual Lead-time', barmode = 'stack', title = 'Customer wise Target and Actual Lead Time') 
            fig.write_image(os.path.join(self.current_month_plots, "customer_wise_target_and_actual_leadtime.png")) 

            fig = sales_instance.stack_or_group_chart(categories='Customer', values = ['HOT'], unit = "%", orientation ='h',
                    sort_by ='HOT', barmode = 'stack', title = 'Customer wise HOT(Handover On-time)') 
            fig.write_image(os.path.join(self.current_month_plots, "customer_wise_hot.png"))

            fig = sales_instance.pareto_chart(categories = 'Customer', values ='Price(USD)', unit="$", unit_position='before', width = 850, height = 600, title = "80/20 Chart of Revenue")
            fig.write_image(os.path.join(self.current_month_plots, "pareto_revenue.png"))

            fig = sales_instance.pareto_chart(categories = 'Customer', values ='Shipped Qty', width = 850, height = 600, title = "80/20 Chart of Quantity")
            fig.write_image(os.path.join(self.current_month_plots, "pareto_qty.png"))
            return self.sales_data
    
    def operational_kpi(self):
            self.get_sales_data(year = [self.current_year_vn])
            self.sales_data.rename(columns={'salesmonth': 'Sales Month', 'shipped_qty':'Shipped Qty',
                                     'custname': 'Customer', 'target_lead_time': 'Target Lead-time',
                                     'actual_lead_time': 'Actual Lead-time', 'delay_days': 'Delay (Days)',
                                     'booking_conf_time':'Booking Confirmation Time', 'lotnumber_x': 'Lot Number'}, inplace = True)
            sales_instance = EDA(self.sales_data)
            fig = sales_instance.area_chart(categories='Sales Month', values = 'Price(USD)', title = 'Monthly Sales Value', aggfunc = 'sum',
                                                        unit = "$", unit_position= 'before', sort_by = 'salesmonth_number')
            fig.write_image(os.path.join(self.operational_plots, "monthly_sales_value.png"))
            fig = sales_instance.area_chart(categories='Sales Month', values = 'Shipped Qty', unit = None, aggfunc='sum',
                                                                sort_by ='salesmonth_number', title = 'Monthly Sales Quantity')
            fig.write_image(os.path.join(self.operational_plots, "monthly_sales_qty.png"))
            fig = sales_instance.piechart(categories='Customer', values = 'Price(USD)',  width = 750, height = 600,
                             title = "Customer wise Revenue Ratio")
            fig.write_image(os.path.join(self.operational_plots, "customer_wise_revenue_ratio.png"))
            fig = sales_instance.piechart(categories='Customer', values = 'Shipped Qty',  width = 750, height = 600,
                             title = "Customer wise Order Qty Ratio")
            fig.write_image(os.path.join(self.operational_plots, "customer_wise_order_qty_ratio.png"))
        
            fig = sales_instance.stack_or_group_chart(categories='Customer', values = ['Target Lead-time', 'Actual Lead-time'], unit = "days", orientation ='h',
                    sort_by ='Actual Lead-time', barmode = 'stack', title = 'Customer wise Target and Actual Lead Time') 
            fig.write_image(os.path.join(self.operational_plots, "customer_wise_target_and_actual_leadtime.png"))                                         
            fig = sales_instance.area_chart(categories='Sales Month', values = 'Delay (Days)', unit = "days", aggfunc='mean',
                                                    sort_by ='salesmonth_number', title = 'Month wise Avg Order Delay')
            fig.write_image(os.path.join(self.operational_plots, "month_wise_avg_order_delay.png"))
            
            fig = sales_instance.stack_or_group_chart(categories='Customer', values = ['HOT'], unit = "%", orientation ='h',
                    sort_by ='HOT', barmode = 'stack', title = 'Customer wise HOT(Handover On-time') 
            fig.write_image(os.path.join(self.operational_plots, "customer_wise_hot.png"))                                       
            fig = sales_instance.area_chart(categories='Sales Month', values = 'HOT', unit = "%", aggfunc='mean',
                                                    sort_by ='salesmonth_number', title = 'Monthly HOT(Handover On-time)')
            fig.write_image(os.path.join(self.operational_plots, "monthly_hot.png"))

            fig = sales_instance.area_chart(categories='Sales Month', values = 'Booking Confirmation Time', unit = "days", aggfunc='mean',
                                                    sort_by ='salesmonth_number', title = 'Monthly Booking Confirmation Time')
            fig.write_image(os.path.join(self.operational_plots, "monthly_booking_confirmation_time.png"))
            fig = sales_instance.combined_corr(x_values='Booking Confirmation Time',y_values = 'Delay (Days)',color='Customer',
                                size = 'Shipped Qty', hover_name='Customer')
            fig.write_image(os.path.join(self.operational_plots, "combined_corr.png"))

            fig = sales_instance.pareto_chart(categories = 'Customer', values ='Price(USD)', unit="$", unit_position='before', width = 850, height = 600, title = "80/20 Chart of Revenue")
            fig.write_image(os.path.join(self.operational_plots, "pareto_revenue.png"))

            fig = sales_instance.pareto_chart(categories = 'Customer', values ='Shipped Qty', width = 850, height = 600, title = "80/20 Chart of Quantity")
            fig.write_image(os.path.join(self.operational_plots, "pareto_qty.png"))
            return self.sales_data