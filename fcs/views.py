# example/views.py
from datetime import datetime

from django.shortcuts import render

from fcs.models import FundCompany, Issuer, Filling

from datetime import datetime, timedelta

import locale

locale.setlocale(locale.LC_ALL, '')

def index(request):
   fund_companies = FundCompany.objects.all()
   issuers = Issuer.objects.all()
   return render(request, "index.html", {'fund_companies': fund_companies, 'issuers': issuers})

def manager(request, slug):
   quart = request.GET.get('q')
   quartC = request.GET.get('c')
   fund_company = FundCompany.objects.get(cik_id = slug)

   positions = Filling.objects.filter(cik_id = slug)
   positions_list = []
   perm_list = []
   for x in positions:
      cusip = x.cusip
      issuer = Issuer.objects.get(cusip = x.cusip).name
      ticker = Issuer.objects.get(cusip = x.cusip).ticker
      value = locale.format_string("%0.2f", float(x.value), grouping=True)
      shares = locale.format_string("%0.2f", float(x.shares), grouping=True)
      date = x.quarter_info
      dater = datetime.strptime(date, "%m-%d-%Y")
      quarter = assign_quarter(dater)
      positions_list.append(ManagerPositionsView(cusip, issuer,ticker, value, shares, date, quarter))
      perm_list.append(ManagerPositionsView(cusip, issuer,ticker, value, shares, date, quarter))
   
   time_series = []
   if((quart is None) == False):
         quart = str(quart).replace("%", " ")
         if(quart != ""):
            positions_list = [value for value in positions_list if value.quarter == quart]
            time_series = [['Issuer', quart]]
            for p in positions_list:
               data = []
               if(p.quarter == quart):
                  data = [p.ticker, int(float(p.value.replace(",","")))]
                  time_series.append(data)                                 
   else:
      quart = "All Quarters"
      title = ['Issuer']
      for q in quarter_list:
         title.append(q)
      time_series = [title]
      headers = time_series[0]

      for p in positions_list:
         issuer_index = headers.index('Issuer')
         q_index = headers.index(p.quarter)
         existing_issuers = [row[0] for row in time_series]
         if(p.ticker in existing_issuers):
            p_index = existing_issuers.index(p.ticker)
            time_series[p_index][q_index] = int(float(p.value.replace(",","")))
         else:
            new_row = [p.ticker] + [0.0] * (q_index - 1) + [int(float(p.value.replace(",","")))] + [0.0] * (len(time_series[0]) - (1 + q_index))
            time_series.append(new_row) 

   comp_list = []
   if((quartC is None) == False):
      quartC = str(quartC).replace("%", " ")
      time_series[0].append(quartC)
      for i in range(1, len(time_series)):
         time_series[i].append(0.0)
      comp_list = [value for value in perm_list if value.quarter == quartC]
      existing_issuers = [row[0] for row in time_series]
      for p in comp_list:
         if(p.ticker in existing_issuers):
            p_index = existing_issuers.index(p.ticker)
            if(p.quarter == quartC):
               time_series[p_index][2] = int(float(p.value.replace(",","")))    
   else:
      quartC = ""

   positions_list = positions_list + comp_list
   return render(request, 'manager.html', {'fund_company': fund_company,
                                           'positions' : positions_list, 
                                           'quarters' : quarter_list,
                                           'quart': quart,
                                           'time_series': time_series,
                                           'quartC': quartC})

def issuer(request, slug):
   quart = request.GET.get('q')
   quartC = request.GET.get('c')
   issuer = Issuer.objects.get(cusip = slug)

   positions = Filling.objects.filter(cusip = slug)
   positions_list = []
   for x in positions:
      cik = x.cik_id
      manager = FundCompany.objects.get(cik_id = x.cik_id).name
      value = locale.format_string("%0.2f", float(x.value), grouping=True)
      shares = locale.format_string("%0.2f", float(x.shares), grouping=True)
      date = x.quarter_info
      dater = datetime.strptime(date, "%m-%d-%Y")
      quarter = assign_quarter(dater)
      positions_list.append(IssuerPositionsView(cik, manager, value, shares, date, quarter))

   comp_data = [['Manager', 'Shares']]
   comp_list = []
   if((quartC is None) == False):
      quartC = str(quartC).replace("%", " ")
      comp_list = [value for value in positions_list if value.quarter == quartC]
      for p in comp_list:
         comp_data.append([p.manager, int(float(p.value.replace(",","")))]) 
   else:
      quartC = ""  

   shares_data = [['Manager', 'Shares']]
   if((quart is None) == False):
      quart = str(quart).replace("%", " ")
      if(quart != ""):
         positions_list = [value for value in positions_list if value.quarter == quart]
         for p in positions_list:
            shares_data.append([p.manager, int(float(p.value.replace(",","")))]) 
   else:
      quart = "All Quarters" 
      for p in positions_list:
         existing_managers = [row[0] for row in shares_data]
         if(p.manager in existing_managers):
            p_index = existing_managers.index(p.manager)
            shares_data[p_index][1] = shares_data[p_index][1] + int(float(p.value.replace(",","")))
         else:
            shares_data.append([p.manager, int(float(p.value.replace(",","")))])
      
   positions_list = positions_list + comp_list
   return render(request, 'issuer.html', {'issuer': issuer, 
                                          'positions' : positions_list, 
                                          'quarters' : quarter_list,
                                          'quart': quart,
                                          'shares_data': shares_data,
                                          'quartC': quartC,
                                          'comp_data': comp_data})

class IssuerPositionsView:
   def __init__(self, cik, manager, value, shares, date, quarter):
    self.cik = cik
    self.manager = manager
    self.value = value
    self.shares = shares
    self.date = date
    self.quarter = quarter

class ManagerPositionsView:
   def __init__(self, cusip, issuer, ticker, value, shares, date, quarter):
    self.cusip = cusip
    self.issuer = issuer
    self.ticker = ticker
    self.value = value
    self.shares = shares
    self.date = date
    self.quarter = quarter    

def assign_quarter(date):
   month = date.month
   year = date.year
   if month in [1, 2, 3]:
      return "Q1 " + str(year)
   elif month in [4, 5, 6]:
      return "Q2 " + str(year)
   elif month in [7, 8, 9]:
      return "Q3 " + str(year)
   else:
      return "Q4 " + str(year)
   
def generate_quarters(num_quarters):
    quarter_list = []
    current_date = datetime.now() - timedelta(days=60)

    for _ in range(num_quarters):
        quarter = f"Q{((current_date.month - 1) // 3) + 1} {current_date.year}"
        quarter_list.append(quarter)
        current_date -= timedelta(days=365 / 4)

    return quarter_list

quarter_list = generate_quarters(20)