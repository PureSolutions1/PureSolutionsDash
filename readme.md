# UPDATING DATA
1. Download csv's in following order:
    - Revenue (1/1/21 - Current)
        - REPORT: Production By Technician
        -  DATE RANGE: (1/1/22 - Current)
        -  SAVE AS: /data/dirty/revenue/revenue_22.csv
    - Sales
        -  REPORT: Sales Report
        -  DATE RANGE: ALL
        -  SAVE AS: /data/dirty/sales_1522.csv
    - Unserviced list
        -  REPORT: Unserviced List
        -  DATE RANGE: (1/1/22 - Current)
        -  SAVE AS: /data/dirty/unserviced_accounts/unserviced_accounts.csv
    - Cancels
        -  REPORT: Customer Cancel Report
        -  DATE RANGE: ALL
        -  SAVE AS: /data/clean/cancels/cancels_1522.csv
    - Route Performance Summary (1/1/22 - Latest) (TICK + MOSQUITO)
        -  REPORT: Route Performance Summary
            -  One with only tick programs
            -  One with only turf programs
        -  DATE RANGE: 1/1/22 -  Current
        -  SAVE AS:
            -  Tick: /data/clean/production/tick_production_analysis.csv
            -  Turf: /data/clean/production/turf_production_analysis.csv
    - Customer Growth (Yearly + monthly)
        -  REPORT: Customer Growth Analysis
        -  DATE RANGE
            -  Monthly: (1st Current Month - Current)
            -  Yearly (1/1/22 - Current)
        -  SAVE AS:
            -  Monthly: /data/clean/customers/cg_monthly.csv
            -  Yearly: /data/clean/customers/cg_yearly.csv
    - Employee Time Card Report
          REPORT: Employee Time Car Report
        -  DATE RANGE: ALL
        -  SAVE AS: /data/clean/employee_hours/employee_hours.csv
    - Product Usage (weekly, monthly, yearly + all time)
        -  REPORT: Product Usage
        -  DATE RANGE:
            -  Weekly: (Sunday of last week - Current)
            -  Monthly: (1st of current month - Current)
            -  Yearly: (1/1/22 - Current)
            -  All Time: (ALL)
        -  SAVE AS:
            -  Weekly: /data/clean/production/product_usage/pu_weekly.csv
            -  Monthly: /data/clean/production/product_usage/pu_monthly.csv
            -  Yearly: /data/clean/production/product_usage/pu_yearly.csv
            -  All Time: /data/clean/production/product_usage/pu_allTime.csv

# DEPLOYMENT
## EASY DEPLOYMENT
NOTE: Must run from command prompt where directory is the PureDash folder. If it is not, the command scripts below will not be able to locate the necessary files.
1. Update Data
    -  Run "git update-data"
2. Deploy
    -  Run "git pure-deploy"
    
OR COMBINE
1. Update + Deploy
    -  run "git update-data && git pure-deploy"

## LONG DEPLOYMENT
1. Update Data: run the following scripts
    -  /cleaner/rev_wash_final.py
    -  /cleaner/sales_wash.py
    -  /cleaner/customer_lifeSpan.py
    -  /cleaner/make_turf_employees_df.py
    -  FOR UPDATING TECH RECAPS:
        1. /cleaner/tech_recaps/make_services_with_addresses.py
        2. /cleaner/tech_recaps/merge_current_and_new.py
        3. /cleaner/tech_recaps/get_the_miles.py
        4. /cleaner/tech_recaps/get_first_services.py
    -  FOR START OF NEW MONTH ONLY:
        Transpose table from MonthlyRevenueGoals in 2021RevenueProjection.xlsx and save into revenue_goals.xlsx
        Convert revenue_goals.xlsx into revenue_goals.csv
