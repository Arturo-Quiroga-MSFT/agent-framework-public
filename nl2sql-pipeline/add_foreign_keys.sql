-- ============================================================
-- Add Foreign Key Constraints to TERADATA-FI Database
-- Star Schema Data Warehouse for Loan/Financial Management
-- ============================================================

USE [TERADATA-FI];
GO

-- ============================================================
-- STEP 1: First, let's examine existing columns in fact tables
-- ============================================================

-- Query to check columns in fact tables
SELECT 
    t.TABLE_SCHEMA,
    t.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.IS_NULLABLE
FROM INFORMATION_SCHEMA.TABLES t
INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
    ON t.TABLE_NAME = c.TABLE_NAME 
    AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
WHERE t.TABLE_SCHEMA = 'fact'
ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION;

-- Query to check primary keys in dimension tables
SELECT 
    t.TABLE_SCHEMA,
    t.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE
FROM INFORMATION_SCHEMA.TABLES t
INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
    ON t.TABLE_NAME = c.TABLE_NAME 
    AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
WHERE t.TABLE_SCHEMA = 'dim'
    AND c.COLUMN_NAME LIKE '%Key'
ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION;
GO

-- ============================================================
-- STEP 2: Add Primary Keys to Dimension Tables (if not exists)
-- ============================================================

-- DimCustomer
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimCustomer')
    ALTER TABLE dim.DimCustomer ADD CONSTRAINT PK_DimCustomer PRIMARY KEY (CustomerKey);

-- DimDate
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimDate')
    ALTER TABLE dim.DimDate ADD CONSTRAINT PK_DimDate PRIMARY KEY (DateKey);

-- DimLoanProduct
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimLoanProduct')
    ALTER TABLE dim.DimLoanProduct ADD CONSTRAINT PK_DimLoanProduct PRIMARY KEY (LoanProductKey);

-- DimLoanPurpose
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimLoanPurpose')
    ALTER TABLE dim.DimLoanPurpose ADD CONSTRAINT PK_DimLoanPurpose PRIMARY KEY (LoanPurposeKey);

-- DimApplicationStatus
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimApplicationStatus')
    ALTER TABLE dim.DimApplicationStatus ADD CONSTRAINT PK_DimApplicationStatus PRIMARY KEY (ApplicationStatusKey);

-- DimRiskRating
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimRiskRating')
    ALTER TABLE dim.DimRiskRating ADD CONSTRAINT PK_DimRiskRating PRIMARY KEY (RiskRatingKey);

-- DimCollateralType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimCollateralType')
    ALTER TABLE dim.DimCollateralType ADD CONSTRAINT PK_DimCollateralType PRIMARY KEY (CollateralTypeKey);

-- DimPaymentMethod
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimPaymentMethod')
    ALTER TABLE dim.DimPaymentMethod ADD CONSTRAINT PK_DimPaymentMethod PRIMARY KEY (PaymentMethodKey);

-- DimPaymentType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimPaymentType')
    ALTER TABLE dim.DimPaymentType ADD CONSTRAINT PK_DimPaymentType PRIMARY KEY (PaymentTypeKey);

-- DimDelinquencyStatus
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimDelinquencyStatus')
    ALTER TABLE dim.DimDelinquencyStatus ADD CONSTRAINT PK_DimDelinquencyStatus PRIMARY KEY (DelinquencyStatusKey);

-- DimInteractionType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimInteractionType')
    ALTER TABLE dim.DimInteractionType ADD CONSTRAINT PK_DimInteractionType PRIMARY KEY (InteractionTypeKey);

-- DimInteractionChannel
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimInteractionChannel')
    ALTER TABLE dim.DimInteractionChannel ADD CONSTRAINT PK_DimInteractionChannel PRIMARY KEY (InteractionChannelKey);

-- DimCovenantType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimCovenantType')
    ALTER TABLE dim.DimCovenantType ADD CONSTRAINT PK_DimCovenantType PRIMARY KEY (CovenantTypeKey);

-- DimStatementType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimStatementType')
    ALTER TABLE dim.DimStatementType ADD CONSTRAINT PK_DimStatementType PRIMARY KEY (StatementTypeKey);

-- DimIndustry
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimIndustry')
    ALTER TABLE dim.DimIndustry ADD CONSTRAINT PK_DimIndustry PRIMARY KEY (IndustryKey);

GO

-- ============================================================
-- STEP 3: Add Foreign Keys to FACT_LOAN_APPLICATION
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_Customer')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Application Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_ApplicationDate')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_ApplicationDate 
    FOREIGN KEY (ApplicationDateKey) REFERENCES dim.DimDate(DateKey);

-- Loan Product
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_LoanProduct')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_LoanProduct 
    FOREIGN KEY (LoanProductKey) REFERENCES dim.DimLoanProduct(LoanProductKey);

-- Loan Purpose
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_LoanPurpose')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_LoanPurpose 
    FOREIGN KEY (LoanPurposeKey) REFERENCES dim.DimLoanPurpose(LoanPurposeKey);

-- Application Status
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_Status')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_Status 
    FOREIGN KEY (ApplicationStatusKey) REFERENCES dim.DimApplicationStatus(ApplicationStatusKey);

GO

-- ============================================================
-- STEP 4: Add Foreign Keys to FACT_LOAN_ORIGINATION
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_Customer')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Origination Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_OriginationDate')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_OriginationDate 
    FOREIGN KEY (OriginationDateKey) REFERENCES dim.DimDate(DateKey);

-- Maturity Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_MaturityDate')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_MaturityDate 
    FOREIGN KEY (MaturityDateKey) REFERENCES dim.DimDate(DateKey);

-- Loan Product
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_LoanProduct')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_LoanProduct 
    FOREIGN KEY (LoanProductKey) REFERENCES dim.DimLoanProduct(LoanProductKey);

-- Loan Purpose
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_LoanPurpose')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_LoanPurpose 
    FOREIGN KEY (LoanPurposeKey) REFERENCES dim.DimLoanPurpose(LoanPurposeKey);

-- Risk Rating
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_RiskRating')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_RiskRating 
    FOREIGN KEY (RiskRatingKey) REFERENCES dim.DimRiskRating(RiskRatingKey);

-- Collateral Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_CollateralType')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_CollateralType 
    FOREIGN KEY (CollateralTypeKey) REFERENCES dim.DimCollateralType(CollateralTypeKey);

GO

-- ============================================================
-- STEP 5: Add Foreign Keys to FACT_PAYMENT_TRANSACTION
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_Customer')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Payment Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_PaymentDate')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_PaymentDate 
    FOREIGN KEY (PaymentDateKey) REFERENCES dim.DimDate(DateKey);

-- Due Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_DueDate')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_DueDate 
    FOREIGN KEY (DueDateKey) REFERENCES dim.DimDate(DateKey);

-- Payment Method
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_PaymentMethod')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_PaymentMethod 
    FOREIGN KEY (PaymentMethodKey) REFERENCES dim.DimPaymentMethod(PaymentMethodKey);

-- Payment Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_PaymentType')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_PaymentType 
    FOREIGN KEY (PaymentTypeKey) REFERENCES dim.DimPaymentType(PaymentTypeKey);

GO

-- ============================================================
-- STEP 6: Add Foreign Keys to FACT_LOAN_BALANCE_DAILY
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanBalance_Customer')
    ALTER TABLE fact.FACT_LOAN_BALANCE_DAILY 
    ADD CONSTRAINT FK_LoanBalance_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Balance Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanBalance_BalanceDate')
    ALTER TABLE fact.FACT_LOAN_BALANCE_DAILY 
    ADD CONSTRAINT FK_LoanBalance_BalanceDate 
    FOREIGN KEY (BalanceDateKey) REFERENCES dim.DimDate(DateKey);

-- Loan Product
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanBalance_LoanProduct')
    ALTER TABLE fact.FACT_LOAN_BALANCE_DAILY 
    ADD CONSTRAINT FK_LoanBalance_LoanProduct 
    FOREIGN KEY (LoanProductKey) REFERENCES dim.DimLoanProduct(LoanProductKey);

-- Delinquency Status
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanBalance_DelinquencyStatus')
    ALTER TABLE fact.FACT_LOAN_BALANCE_DAILY 
    ADD CONSTRAINT FK_LoanBalance_DelinquencyStatus 
    FOREIGN KEY (DelinquencyStatusKey) REFERENCES dim.DimDelinquencyStatus(DelinquencyStatusKey);

-- Risk Rating
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanBalance_RiskRating')
    ALTER TABLE fact.FACT_LOAN_BALANCE_DAILY 
    ADD CONSTRAINT FK_LoanBalance_RiskRating 
    FOREIGN KEY (RiskRatingKey) REFERENCES dim.DimRiskRating(RiskRatingKey);

GO

-- ============================================================
-- STEP 7: Add Foreign Keys to FACT_CUSTOMER_INTERACTION
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_Customer')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Interaction Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_InteractionDate')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_InteractionDate 
    FOREIGN KEY (InteractionDateKey) REFERENCES dim.DimDate(DateKey);

-- Interaction Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_InteractionType')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_InteractionType 
    FOREIGN KEY (InteractionTypeKey) REFERENCES dim.DimInteractionType(InteractionTypeKey);

-- Interaction Channel
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_InteractionChannel')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_InteractionChannel 
    FOREIGN KEY (InteractionChannelKey) REFERENCES dim.DimInteractionChannel(InteractionChannelKey);

GO

-- ============================================================
-- STEP 8: Add Foreign Keys to FACT_COVENANT_TEST
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Covenant_Customer')
    ALTER TABLE fact.FACT_COVENANT_TEST 
    ADD CONSTRAINT FK_Covenant_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Test Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Covenant_TestDate')
    ALTER TABLE fact.FACT_COVENANT_TEST 
    ADD CONSTRAINT FK_Covenant_TestDate 
    FOREIGN KEY (TestDateKey) REFERENCES dim.DimDate(DateKey);

-- Covenant Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Covenant_CovenantType')
    ALTER TABLE fact.FACT_COVENANT_TEST 
    ADD CONSTRAINT FK_Covenant_CovenantType 
    FOREIGN KEY (CovenantTypeKey) REFERENCES dim.DimCovenantType(CovenantTypeKey);

GO

-- ============================================================
-- STEP 9: Add Foreign Keys to FACT_CUSTOMER_FINANCIALS
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Financials_Customer')
    ALTER TABLE fact.FACT_CUSTOMER_FINANCIALS 
    ADD CONSTRAINT FK_Financials_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Statement Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Financials_StatementDate')
    ALTER TABLE fact.FACT_CUSTOMER_FINANCIALS 
    ADD CONSTRAINT FK_Financials_StatementDate 
    FOREIGN KEY (StatementDateKey) REFERENCES dim.DimDate(DateKey);

-- Statement Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Financials_StatementType')
    ALTER TABLE fact.FACT_CUSTOMER_FINANCIALS 
    ADD CONSTRAINT FK_Financials_StatementType 
    FOREIGN KEY (StatementTypeKey) REFERENCES dim.DimStatementType(StatementTypeKey);

GO

-- ============================================================
-- STEP 10: Add Foreign Key from DimCustomer to DimIndustry
-- ============================================================

-- Industry (dimension-to-dimension relationship)
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Customer_Industry')
    ALTER TABLE dim.DimCustomer 
    ADD CONSTRAINT FK_Customer_Industry 
    FOREIGN KEY (IndustryKey) REFERENCES dim.DimIndustry(IndustryKey);

GO

-- ============================================================
-- STEP 11: Verify all foreign keys were created
-- ============================================================

SELECT 
    fk.name AS ForeignKeyName,
    OBJECT_SCHEMA_NAME(fk.parent_object_id) AS TableSchema,
    OBJECT_NAME(fk.parent_object_id) AS TableName,
    COL_NAME(fc.parent_object_id, fc.parent_column_id) AS ColumnName,
    OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS ReferencedSchema,
    OBJECT_NAME(fk.referenced_object_id) AS ReferencedTable,
    COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS ReferencedColumn
FROM sys.foreign_keys AS fk
INNER JOIN sys.foreign_key_columns AS fc 
    ON fk.object_id = fc.constraint_object_id
WHERE OBJECT_SCHEMA_NAME(fk.parent_object_id) IN ('dim', 'fact')
ORDER BY TableSchema, TableName, ForeignKeyName;

GO

PRINT 'Foreign key constraints added successfully!';
PRINT 'The database now has a complete star schema with enforced referential integrity.';
