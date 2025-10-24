# TERADATA-FI — NL→SQL Test Cases (nl2sql)

This file documents the schema inspection and a set of natural-language test questions (easy / medium / hard) with target SQL for the TERADATA-FI database. Use these as a test-suite for NL→SQL generators and executors. Prefer running read-only queries (SELECT) against a test user.

## Quick inspection summary

- Server: aqsqlserver001.database.windows.net
- Database: TERADATA-FI
- Representative schemas: `dim`, `fact`

Key tables inspected:

- `fact.FACT_LOAN_ORIGINATION` — 43 columns. Important columns:
  - LoanKey, LoanId, CustomerKey, OriginationDateKey, MaturityDateKey, FirstPaymentDateKey
  - OriginalAmount, FundedAmount, CurrentBalance, PrincipalPaid, InterestPaid
  - TermMonths, RemainingTermMonths, InterestRate, RateType, ReferenceRate, Margin, APR
  - PaymentsMade, PaymentsScheduled, MissedPayments, LatePayments, DaysDelinquent
  - NPV, IRR, ROE, Yield
  - IsActive, IsPaidOff, IsChargedOff, IsRestructured, HasPersonalGuarantee
  - CreatedDate, ModifiedDate

- `fact.FACT_PAYMENT_TRANSACTION` — 21 columns. Important columns:
  - PaymentKey, PaymentId, LoanKey, PaymentDateKey, ScheduledDateKey
  - PaymentMethodKey, PaymentTypeKey
  - TotalPaymentAmount, PrincipalAmount, InterestAmount, FeesAmount, PenaltyAmount
  - ScheduledAmount, PaymentNumber, DaysLate
  - IsEarlyPayment, IsLatePayment, IsPrepayment, IsReversed
  - CreatedDate, ModifiedDate

- `dim.DimCustomer` — customer master table with columns like:
  - CustomerKey, CustomerId (e.g. CUST00001), CompanyName, TaxId, LegalEntityType
  - YearFounded, EmployeeCount, AnnualRevenue, PrimaryIndustryId, PrimarySICCode, PrimaryNAICSCode
  - CreditRating_SP, CreditRating_Moody, CreditRating_Fitch, InternalRiskRating
  - CustomerSegment, CustomerTier, TotalLoansCount, TotalLoanVolume, LifetimeRevenue
  - DefaultCount, IsActive, IsHighRisk, IsVIP, EffectiveDate, IsCurrent

- `dim.DimDate` — date dimension with columns:
  - DateKey, Date, Year, Quarter, Month, MonthName, Week, DayOfYear, DayOfMonth, DayOfWeek
  - DayName, IsWeekend, IsHoliday, HolidayName, IsQuarterEnd, IsYearEnd, IsMonthEnd
  - FiscalYear, FiscalQuarter, FiscalMonth, PriorDay, PriorWeek, PriorMonth, PriorQuarter, PriorYear

## Sampled values (from `dim.DimCustomer` top 10 rows)
- CustomerId examples: `CUST00001`, `CUST00002`, ..., `CUST00010`
- CompanyName examples: "Johnson Manufacturing Inc", "Smith Healthcare Systems", "Williams Auto Parts Corp"
- AnnualRevenue examples: 12500000.00, 28000000.00, etc.
- TotalLoansCount: small integers (1..15)
- TotalLoanVolume: numeric values (e.g. 8500000.00)
- IsVIP values: 0/1

## NL→SQL test cases
Below are grouped prompts by focus area and difficulty. Each includes: NL text, target SQL, and notes.

---

### Loans

Easy — Show active loans

NL:
"Show me the loan id and current balance for all active loans."

SQL:
```sql
SELECT LoanId, CurrentBalance
FROM fact.FACT_LOAN_ORIGINATION
WHERE IsActive = 1;
```
Notes: Uses bit column `IsActive`. Expect non-empty results.


Medium — High-balance loans by interest

NL:
"Give me loans with OriginalAmount over 1,000,000 and show LoanId, OriginalAmount, InterestRate, and TermMonths, ordered by OriginalAmount descending."

SQL:
```sql
SELECT LoanId, OriginalAmount, InterestRate, TermMonths
FROM fact.FACT_LOAN_ORIGINATION
WHERE OriginalAmount > 1000000
ORDER BY OriginalAmount DESC;
```
Notes: Numeric comparison and ordering.


Hard — Cohort delinquency analysis

NL:
"For each customer, find the number of loans they have that are currently delinquent (DaysDelinquent > 0), and list customers with at least one delinquent loan. Return CustomerKey, count of delinquent loans, and total CurrentBalance of those delinquent loans."

SQL:
```sql
SELECT dlo.CustomerKey,
       COUNT(*) AS DelinquentLoanCount,
       SUM(dlo.CurrentBalance) AS DelinquentTotalBalance
FROM fact.FACT_LOAN_ORIGINATION dlo
WHERE dlo.DaysDelinquent > 0
GROUP BY dlo.CustomerKey
HAVING COUNT(*) > 0;
```
Notes: Grouping and HAVING. NULL handling for DaysDelinquent should be considered.

---

### Payments

Easy — Recent payments

NL:
"Show the most recent 10 payments with PaymentId, LoanKey, TotalPaymentAmount, and PaymentDateKey."

SQL:
```sql
SELECT TOP 10 PaymentId, LoanKey, TotalPaymentAmount, PaymentDateKey
FROM fact.FACT_PAYMENT_TRANSACTION
ORDER BY PaymentKey DESC;
```
Notes: If PaymentDateKey is available and sortable, prefer ORDER BY PaymentDateKey DESC.


Medium — Late payment rate per loan

NL:
"For each loan, compute the number of late payments and total payments, and return LoanKey, LatePayments, TotalPayments, and LatePaymentRate (LatePayments/TotalPayments) for loans with at least 5 payments."

SQL:
```sql
SELECT p.LoanKey,
       SUM(CASE WHEN p.IsLatePayment = 1 THEN 1 ELSE 0 END) AS LatePayments,
       COUNT(*) AS TotalPayments,
       CAST(SUM(CASE WHEN p.IsLatePayment = 1 THEN 1 ELSE 0 END) AS decimal(9,4)) / COUNT(*) AS LatePaymentRate
FROM fact.FACT_PAYMENT_TRANSACTION p
GROUP BY p.LoanKey
HAVING COUNT(*) >= 5;
```
Notes: Avoid divide-by-zero with HAVING; watch integer division.


Hard — Payment trend over time for top customers

NL:
"For the top 5 customers by TotalLoanVolume in `dim.DimCustomer`, show monthly total payments (sum of TotalPaymentAmount) for the last 12 months. Return CustomerKey, Year, Month, MonthName, TotalMonthlyPayments, ordered by CustomerKey and Year,Month."

SQL (conceptual; adapt joins to your schema):
```sql
WITH TopCustomers AS (
  SELECT CustomerKey
  FROM dim.DimCustomer
  ORDER BY TotalLoanVolume DESC
  OFFSET 0 ROWS FETCH NEXT 5 ROWS ONLY
),
Payments AS (
  SELECT p.LoanKey, p.TotalPaymentAmount, d.Year, d.Month, d.MonthName
  FROM fact.FACT_PAYMENT_TRANSACTION p
  JOIN fact.FACT_LOAN_ORIGINATION dimLoan ON p.LoanKey = dimLoan.LoanKey
  JOIN dim.DimDate d ON p.PaymentDateKey = d.DateKey
)
SELECT tl.CustomerKey, pay.Year, pay.Month, pay.MonthName, SUM(pay.TotalPaymentAmount) AS TotalMonthlyPayments
FROM Payments pay
JOIN fact.FACT_LOAN_ORIGINATION dimLoan ON pay.LoanKey = dimLoan.LoanKey
JOIN TopCustomers tl ON dimLoan.CustomerKey = tl.CustomerKey
WHERE (pay.Year > DATEPART(year, DATEADD(month, -12, GETDATE()))
       OR (pay.Year = DATEPART(year, DATEADD(month, -12, GETDATE())) AND pay.Month >= DATEPART(month, DATEADD(month, -12, GETDATE()))))
GROUP BY tl.CustomerKey, pay.Year, pay.Month, pay.MonthName
ORDER BY tl.CustomerKey, pay.Year, pay.Month;
```
Notes: This assumes the payment->loan->customer linkage exists via LoanKey; adjust date filter to use DateKey ranges for production.

---

### Customers

Easy — Find customers by name snippet

NL:
"Find customers whose company name contains 'Healthcare' and show CustomerId, CompanyName, AnnualRevenue."

SQL:
```sql
SELECT CustomerId, CompanyName, AnnualRevenue
FROM dim.DimCustomer
WHERE CompanyName LIKE '%Healthcare%';
```
Notes: Collation affects case-sensitivity.


Medium — High value VIP customers

NL:
"List VIP customers (IsVIP = 1) with TotalLoansCount, TotalLoanVolume, and LifetimeRevenue, sorted by LifetimeRevenue descending."

SQL:
```sql
SELECT CustomerId, CompanyName, TotalLoansCount, TotalLoanVolume, LifetimeRevenue
FROM dim.DimCustomer
WHERE IsVIP = 1
ORDER BY LifetimeRevenue DESC;
```

Hard — Customers with rising delinquency

NL:
"Find customers who had zero delinquent loans last year but have at least one delinquent loan this year. Return CustomerKey, CustomerId, CompanyName, LastYearDelinquentCount, ThisYearDelinquentCount."

SQL (conceptual; may need snapshots or alternate date mapping):
```sql
WITH LoanDelinquencies AS (
  SELECT lo.CustomerKey,
         CASE WHEN d.Year = YEAR(DATEADD(year, -1, GETDATE())) THEN 'last' WHEN d.Year = YEAR(GETDATE()) THEN 'this' END AS Period,
         CASE WHEN lo.DaysDelinquent > 0 THEN 1 ELSE 0 END AS IsDelinquent
  FROM fact.FACT_LOAN_ORIGINATION lo
  JOIN dim.DimDate d ON lo.OriginationDateKey = d.DateKey
  WHERE d.Year IN (YEAR(DATEADD(year, -1, GETDATE())), YEAR(GETDATE()))
),
Aggregated AS (
  SELECT CustomerKey, Period, SUM(IsDelinquent) AS DelinquentCount
  FROM LoanDelinquencies
  GROUP BY CustomerKey, Period
)
SELECT a.CustomerKey, c.CustomerId, c.CompanyName,
       ISNULL(l.DelinqCount,0) AS LastYearDelinquentCount,
       ISNULL(t.DelinqCount,0) AS ThisYearDelinquentCount
FROM (SELECT DISTINCT CustomerKey FROM Aggregated) a
LEFT JOIN Aggregated l ON a.CustomerKey = l.CustomerKey AND l.Period = 'last'
LEFT JOIN Aggregated t ON a.CustomerKey = t.CustomerKey AND t.Period = 'this'
JOIN dim.DimCustomer c ON a.CustomerKey = c.CustomerKey
WHERE ISNULL(l.DelinqCount,0) = 0 AND ISNULL(t.DelinqCount,0) > 0;
```
Notes: Use snapshots if available (LoanDelinquencyFeaturesSnapshot) for accurate time-series delinquency.

---

### Time / Cross-cutting

Easy — Payments in a month

NL:
"How much was paid in total in July 2025?"

SQL:
```sql
SELECT SUM(p.TotalPaymentAmount) AS TotalPaid
FROM fact.FACT_PAYMENT_TRANSACTION p
JOIN dim.DimDate d ON p.PaymentDateKey = d.DateKey
WHERE d.Year = 2025 AND d.Month = 7;
```

Medium — Monthly new loans trend

NL:
"Show the number of loans originated each month for the last 6 months (MonthName, Year, LoanCount)."

SQL:
```sql
SELECT d.Year, d.Month, d.MonthName, COUNT(*) AS LoanCount
FROM fact.FACT_LOAN_ORIGINATION lo
JOIN dim.DimDate d ON lo.OriginationDateKey = d.DateKey
WHERE d.Date >= DATEADD(month, -6, CAST(GETDATE() AS date))
GROUP BY d.Year, d.Month, d.MonthName
ORDER BY d.Year, d.Month;
```

Hard — Defaulted loan exposure by industry

NL:
"For each industry, compute the total current balance of charged-off loans (IsChargedOff = 1) and the percentage of charged-off balance relative to total loan balance for that industry. Return IndustryName, ChargedOffBalance, TotalBalance, ChargedOffPct, sorted by ChargedOffPct desc."

SQL (conceptual - verify FK names):
```sql
SELECT ind.DimIndustryName AS IndustryName,
       SUM(CASE WHEN lo.IsChargedOff = 1 THEN lo.CurrentBalance ELSE 0 END) AS ChargedOffBalance,
       SUM(lo.CurrentBalance) AS TotalBalance,
       CASE WHEN SUM(lo.CurrentBalance) = 0 THEN 0
            ELSE CAST(SUM(CASE WHEN lo.IsChargedOff = 1 THEN lo.CurrentBalance ELSE 0 END) AS decimal(18,4)) / SUM(lo.CurrentBalance)
       END AS ChargedOffPct
FROM fact.FACT_LOAN_ORIGINATION lo
JOIN dim.DimIndustry ind ON lo.PrimaryIndustryId = ind.IndustryKey -- adjust FK column name
GROUP BY ind.DimIndustryName
ORDER BY ChargedOffPct DESC;
```
Notes: Confirm `PrimaryIndustryId` FK and `DimIndustry` column names.

---

## Validation and test recommendations
- Start with easy queries and inspect results and data types. Use `TOP N` and date limits to avoid heavy scans.
- For medium/hard queries, validate join keys (LoanKey -> CustomerKey mapping) and date mapping (DateKey). Adjust queries to use snapshots if time-series accuracy is required.
- Handle NULLs using ISNULL or COALESCE where aggregates are sensitive to NULL values.
- Use `SET TRANSACTION ISOLATION LEVEL` or read-only users for safety if tests run in production-like environments.

## Next steps I can do for you
- Execute selected read-only SQL queries and return results.
- Export the test cases to CSV/JSON for automated runs.
- Add negative/ambiguous NL prompts to test generator robustness.

---

File created by automation on 2025-10-17.
